# -*- coding: utf-8 -*-
"""Generate ERP health findings and scores."""

from odoo import fields, models


class RnErpHealthScanService(models.AbstractModel):
    _name = 'rn.erp.health.scan.service'
    _description = 'ERP Health Scan Service'

    def run_scan(self, target):
        scan = self.env['rn.erp.health.scan'].create({
            'target_id': target.id,
            'state': 'running',
            'started_at': fields.Datetime.now(),
            'name': self.env['ir.sequence'].next_by_code('rn.erp.health.scan') or 'New',
        })
        findings = self._collect_findings(target)
        for finding in findings:
            finding['scan_id'] = scan.id
            self.env['rn.erp.health.finding'].create(finding)
        score = max(0, 100 - sum(scan.finding_ids.mapped('score_impact')))
        scan.write({
            'state': 'done',
            'completed_at': fields.Datetime.now(),
            'overall_score': score,
            'risk_level': self._get_risk_level(score),
            'summary': self._build_summary(scan),
        })
        target.write({
            'last_scan_id': scan.id,
            'last_score': score,
        })
        return scan

    def _collect_findings(self, target):
        findings = []
        findings.extend(self._performance_findings(target))
        findings.extend(self._security_findings(target))
        findings.extend(self._data_quality_findings(target))
        findings.extend(self._accounting_findings(target))
        findings.extend(self._module_findings(target))
        if not findings:
            findings.append({
                'name': 'No major issues detected in current quick scan',
                'code': 'scan.clean',
                'category': 'operations',
                'severity': 'info',
                'score_impact': 0,
                'recommendation': 'Keep weekly scans enabled and review trend reports.',
                'technical_details': 'Quick scan completed without threshold breaches.',
            })
        return findings

    def _performance_findings(self, target):
        findings = []
        cron_count = self.env['ir.cron'].sudo().search_count([('active', '=', True)])
        if cron_count > 40:
            findings.append({
                'name': 'High number of active scheduled jobs',
                'code': 'performance.cron_volume',
                'category': 'performance',
                'severity': 'medium' if cron_count < 80 else 'high',
                'score_impact': 8 if cron_count < 80 else 14,
                'model_name': 'ir.cron',
                'metric_value': cron_count,
                'recommendation': 'Review duplicate or obsolete scheduled jobs and stagger heavy jobs.',
                'technical_details': f'Active scheduled jobs detected: {cron_count}.',
            })
        attachment_count = self.env['ir.attachment'].sudo().search_count([])
        if attachment_count > 5000:
            findings.append({
                'name': 'Attachment volume may affect storage and backups',
                'code': 'performance.attachments_growth',
                'category': 'performance',
                'severity': 'medium',
                'score_impact': 6,
                'model_name': 'ir.attachment',
                'metric_value': attachment_count,
                'recommendation': 'Archive obsolete files and review external object storage options.',
                'technical_details': f'Attachment count is {attachment_count}.',
            })
        return findings

    def _security_findings(self, target):
        findings = []
        admin_group = self.env.ref('base.group_system')
        admin_count = self.env['res.users'].sudo().search_count([
            ('group_ids', 'in', admin_group.ids),
            ('share', '=', False),
            ('active', '=', True),
        ])
        if admin_count > 3:
            findings.append({
                'name': 'Too many active system administrators',
                'code': 'security.admin_sprawl',
                'category': 'security',
                'severity': 'high',
                'score_impact': 15,
                'model_name': 'res.users',
                'metric_value': admin_count,
                'recommendation': 'Reduce system admin access and assign least-privilege roles.',
                'technical_details': f'Active internal admins detected: {admin_count}.',
            })
        portal_admins = self.env['res.users'].sudo().search_count([
            ('share', '=', True),
            ('group_ids', 'in', admin_group.ids),
        ])
        if portal_admins:
            findings.append({
                'name': 'Portal users with system administration rights detected',
                'code': 'security.portal_admin',
                'category': 'security',
                'severity': 'critical',
                'score_impact': 25,
                'model_name': 'res.users',
                'metric_value': portal_admins,
                'recommendation': 'Remove administration rights from shared users immediately.',
                'technical_details': f'Portal admins detected: {portal_admins}.',
            })
        return findings

    def _data_quality_findings(self, target):
        findings = []
        partners = self.env['res.partner'].sudo().search([
            ('email', '!=', False),
            ('company_id', 'in', [False, target.company_id.id]),
        ])
        email_counts = {}
        for partner in partners:
            email = (partner.email or '').strip().lower()
            if email:
                email_counts[email] = email_counts.get(email, 0) + 1
        duplicate_count = len([count for count in email_counts.values() if count > 1])
        if duplicate_count:
            findings.append({
                'name': 'Duplicate customer email patterns found',
                'code': 'data.duplicate_emails',
                'category': 'data_quality',
                'severity': 'medium',
                'score_impact': 7,
                'model_name': 'res.partner',
                'metric_value': duplicate_count,
                'recommendation': 'Review duplicate contacts and merge customer master records where valid.',
                'technical_details': f'Duplicate email groups found: {duplicate_count}.',
            })
        missing_customer_email = self.env['res.partner'].sudo().search_count([
            ('customer_rank', '>', 0),
            ('email', '=', False),
            ('company_id', 'in', [False, target.company_id.id]),
        ])
        if missing_customer_email > 10:
            findings.append({
                'name': 'Many customer records are missing email addresses',
                'code': 'data.customer_email_missing',
                'category': 'data_quality',
                'severity': 'low',
                'score_impact': 4,
                'model_name': 'res.partner',
                'metric_value': missing_customer_email,
                'recommendation': 'Improve customer master completeness to support communication and collections.',
                'technical_details': f'Customers without email: {missing_customer_email}.',
            })
        return findings

    def _accounting_findings(self, target):
        findings = []
        aml_domain = [('parent_state', '=', 'posted'), ('reconciled', '=', False), ('account_type', 'in', ('asset_receivable', 'liability_payable'))]
        unreconciled_count = self.env['account.move.line'].sudo().search_count(aml_domain)
        if unreconciled_count > 50:
            findings.append({
                'name': 'Large unreconciled receivable and payable backlog',
                'code': 'accounting.unreconciled_backlog',
                'category': 'accounting',
                'severity': 'medium' if unreconciled_count < 200 else 'high',
                'score_impact': 8 if unreconciled_count < 200 else 14,
                'model_name': 'account.move.line',
                'metric_value': unreconciled_count,
                'recommendation': 'Review collection and reconciliation process, then clear old open items.',
                'technical_details': f'Open receivable and payable lines: {unreconciled_count}.',
            })
        return findings

    def _module_findings(self, target):
        findings = []
        installed_modules = self.env['ir.module.module'].sudo().search_count([('state', '=', 'installed')])
        if installed_modules > 180:
            findings.append({
                'name': 'Installed module volume increases maintenance complexity',
                'code': 'modules.installed_volume',
                'category': 'modules',
                'severity': 'medium',
                'score_impact': 7,
                'model_name': 'ir.module.module',
                'metric_value': installed_modules,
                'recommendation': 'Review unused modules and isolate overlapping customizations before upgrades.',
                'technical_details': f'Installed modules detected: {installed_modules}.',
            })
        custom_modules = self.env['ir.module.module'].sudo().search_count([
            ('state', '=', 'installed'),
            ('name', '=like', 'rn_%'),
        ])
        if custom_modules > 20:
            findings.append({
                'name': 'High custom module footprint raises upgrade risk',
                'code': 'upgrade.custom_module_risk',
                'category': 'upgrade',
                'severity': 'high',
                'score_impact': 12,
                'model_name': 'ir.module.module',
                'metric_value': custom_modules,
                'recommendation': 'Prioritize dependency mapping and regression tests before major upgrades.',
                'technical_details': f'Installed custom rn_ modules detected: {custom_modules}.',
            })
        return findings

    def _get_risk_level(self, score):
        if score >= 85:
            return 'low'
        if score >= 70:
            return 'medium'
        if score >= 50:
            return 'high'
        return 'critical'

    def _build_summary(self, scan):
        critical = len(scan.finding_ids.filtered(lambda f: f.severity == 'critical'))
        high = len(scan.finding_ids.filtered(lambda f: f.severity == 'high'))
        return (
            f'ERP health score {scan.overall_score:.0f}/100. '
            f'Critical findings: {critical}. High findings: {high}. '
            f'Total findings: {scan.finding_count}.'
        )
