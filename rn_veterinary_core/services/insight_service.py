# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetInsightService(models.AbstractModel):
    _name = 'rn.vet.insight.service'
    _description = 'Veterinary AI Insight Service'

    def draft_clinical_note(self, record_id):
        rec = self.env['rn.vet.medical.record'].browse(record_id)
        rec.ensure_one()
        pet = rec.pet_id
        return (
            f'Pet: {pet.name} ({pet.species}, {pet.breed or "mixed"}). '
            f'Weight: {pet.weight_kg or "-"} kg. '
            f'Diagnosis: {rec.diagnosis or "Routine exam"}. '
            f'Prescription: {rec.prescription or "None"}.'
        )

    def vaccination_reminder_message(self, pet_id):
        pet = self.env['rn.vet.pet'].browse(pet_id)
        due = self.env['rn.vet.vaccination'].search([
            ('pet_id', '=', pet_id),
            ('next_due_date', '<=', fields.Date.context_today(self)),
        ], limit=1)
        if due:
            return f'Reminder: {pet.name} is due for {due.vaccine_type_id.name}. Please book an appointment.'
        return f'{pet.name} has no overdue vaccinations on record.'

    def answer_business_question(self, question, company_id=None):
        q = (question or '').lower()
        company_id = company_id or self.env.company.id
        dash = self.env['rn.vet.dashboard.service'].get_clinic_dashboard(company_id)
        if 'vaccin' in q:
            return f'{dash["vaccinations_due"]} vaccinations due within 14 days.'
        if 'board' in q or 'kennel' in q:
            return f'Boarding occupancy: {dash["boarding_occupancy"]}% ({dash["kennels_occupied"]} kennels in use).'
        if 'breed' in q or 'species' in q:
            pets = self.env['rn.vet.pet'].read_group(
                [('company_id', '=', company_id), ('active', '=', True)],
                ['species'],
                ['species'],
            )
            if pets:
                top = max(pets, key=lambda p: p['species_count'])
                return f'Most common species: {top["species"]} ({top["species_count"]} pets).'
        if 'appointment' in q:
            return f'{dash["appointments_today"]} appointments scheduled today.'
        return (
            f'Appointments today: {dash["appointments_today"]}. '
            f'Vaccinations due: {dash["vaccinations_due"]}. '
            f'Active pets: {dash["pet_count"]}.'
        )

    def suggest_vaccines(self, pet_id):
        vaccines = self.env['rn.vet.vaccination.service'].suggest_for_pet(pet_id)
        return {
            'suggested': vaccines.mapped('name'),
            'note': 'Heuristic suggestion based on species and vaccination history.',
        }
