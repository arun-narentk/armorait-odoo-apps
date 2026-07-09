# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelInsightService(models.AbstractModel):
    _name = 'rn.hotel.insight.service'
    _description = 'Hotel AI Insight Service'

    def suggest_rate(self, room_type_id, check_in, check_out):
        room_type = self.env['rn.hotel.room.type'].browse(room_type_id)
        base = room_type.base_rate or 0.0
        board = self.env['rn.hotel.dashboard.service'].get_gm_dashboard()
        occupancy = board.get('occupancy_pct', 0)
        adjustment = 0.0
        if occupancy > 85:
            adjustment = 0.15
        elif occupancy > 70:
            adjustment = 0.08
        elif occupancy < 40:
            adjustment = -0.10
        suggested = round(base * (1 + adjustment), 2)
        return {
            'base_rate': base,
            'suggested_rate': suggested,
            'occupancy_pct': occupancy,
            'note': 'AI pricing suggestion. Staff must approve before publishing.',
        }

    def concierge_reply(self, message):
        msg = (message or '').lower()
        if 'late checkout' in msg or 'checkout' in msg:
            return 'Late checkout is subject to availability. Please contact reception.'
        if 'taxi' in msg or 'cab' in msg:
            return 'We can arrange a taxi. Share your pickup time at reception.'
        if 'restaurant' in msg or 'table' in msg:
            return 'Restaurant reservations can be made at reception or via room service.'
        if 'nearby' in msg or 'attraction' in msg:
            return 'Reception can share local recommendations and maps.'
        return 'Thank you for your message. Our team will assist you shortly.'

    def answer_revenue_question(self, question, company_id=None):
        q = (question or '').lower()
        dash = self.env['rn.hotel.dashboard.service'].get_gm_dashboard(company_id)
        if 'occupancy' in q:
            return f"Current occupancy is {dash['occupancy_pct']}% ({dash['occupied_rooms']}/{dash['total_rooms']} rooms)."
        if 'adr' in q or 'rate' in q:
            return f"Estimated ADR today is {dash['adr']}."
        if 'revenue' in q:
            return f"Revenue posted today is {dash['revenue_today']}."
        if 'dirty' in q or 'housekeeping' in q:
            return f"There are {dash['dirty_rooms']} rooms needing housekeeping attention."
        return (
            f"Occupancy {dash['occupancy_pct']}%, arrivals {dash['arrivals_today']}, "
            f"departures {dash['departures_today']}."
        )
