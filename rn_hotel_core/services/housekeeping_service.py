# -*- coding: utf-8 -*-

from odoo import models


class RnHotelHousekeepingService(models.AbstractModel):
    _name = 'rn.hotel.housekeeping.service'
    _description = 'Housekeeping Service'

    def create_task_from_checkout(self, room_id):
        room = self.env['rn.hotel.room'].browse(room_id)
        return self.env['rn.hotel.housekeeping.task'].create({
            'name': f'Clean room {room.name}',
            'room_id': room.id,
            'state': 'dirty',
        }).id

    def assign_task(self, task_id, employee_id):
        task = self.env['rn.hotel.housekeeping.task'].browse(task_id)
        task.write({'assigned_to': employee_id, 'state': 'assigned'})
        task.room_id.status = 'cleaning'
        return True

    def complete_cleaning(self, task_id):
        task = self.env['rn.hotel.housekeeping.task'].browse(task_id)
        task.state = 'inspection'
        return True

    def approve_inspection(self, task_id):
        task = self.env['rn.hotel.housekeeping.task'].browse(task_id)
        task.state = 'done'
        task.room_id.status = 'vacant'
        return True
