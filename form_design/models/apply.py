from odoo import models, fields, api, _
from odoo.exceptions import UserError
from calendar import monthrange

WeakDays = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


class ApplyFormDesign(models.Model):
    _name = 'form.apply'
    _description = 'Form Apply'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'complete_name'
    _sql_constraints = [
        ('form_partner_day_uniq', 'unique(form_id, partner_id, date)',
         'This form already exist'),

    ]
    category = fields.Many2one('partner.category','Partner Category',related='form_id.category')
    form_id = fields.Many2one('form.design', 'Form', store=True, index=True, tracking=True, required=1)
    partner_id = fields.Many2one('res.partner', 'Partner', domain="[('category','=',category)]", store=True, index=True, tracking=True, required=1)
    apply_ids = fields.One2many('form.apply.line', 'apply_id', store=True, index=True, tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Closed')], default='draft', store=True,
                             tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True, store=True, index=True, required=1)
    complete_name = fields.Char('Name', compute='_compute_name', store=True, index=True, tracking=True)
    allow_add = fields.Boolean("Allow Add Line", compute="compute_allow_add_line")

    def view_form_fill_in_line(self):
        return {
            'name': _('Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'form.apply.line',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.apply_ids.ids)],
            'context': self.env.context,
        }

    @api.depends('form_id', 'date', 'partner_id')
    def _compute_name(self):
        for record in self:
            name = ''
            if record.form_id:
                name += record.form_id.name
            if record.partner_id:
                name += ' ' + record.partner_id.name
            if record.date:
                name += ' ' + str(record.date)
            record.complete_name = name

    def set_close(self):
        self.state = 'done'

    @api.onchange('form_id')
    def form_change(self):
        form_lines = self.apply_ids.filtered(lambda l: l.form_id == self.form_id)
        if self.state == 'draft' and not form_lines:
            self.apply_ids.unlink()
            lines = []
            for line in self.form_id.question_ids:

                lines.append((0, 0, {
                    'name': line.title,
                    'sequence': line.sequence,
                    'form_line_id': line.id,
                    'form_id': self.form_id.id,
                    'question_type': line.question_type,
                    'matrix_answer_type': line.matrix_answer_type,
                }))
                print(line.matrix_answer_type)
            self.write({'apply_ids': lines})

    @api.onchange("form_id")
    def compute_allow_add_line(self):
        for record in self:
            if record.form_id:
                record.allow_add = record.form_id.allow_add
            else:
                record.allow_add = False

    def action_done(self):
        self.state = 'done'

    def confirm(self):
        if self.apply_ids.filtered(lambda line: not line.answer or line.question_type == 'matrix'):
            return {
                'name': _('Answers'),
                'type': 'ir.actions.act_window',
                'res_model': 'form.apply.line',
                'view_mode': 'form',
                'view_id': self.env.ref('form_design.form_apply_line_form_view2').id,
                'res_id': self.apply_ids.filtered(lambda line: not line.answer or line.question_type == 'matrix')[0].id,
                'target': 'new',
                'domain': [('id', '=', self.apply_ids.filtered(lambda line: not line.answer or line.question_type == 'matrix')[0].id)],
                'context': self.env.context,
            }

    def add_line(self):
        if self.form_id.question_ids:
            return {
                'name': _('Answers'),
                'type': 'ir.actions.act_window',
                'res_model': 'form.apply.line',
                'view_mode': 'form',
                'view_id': self.env.ref('form_design.form_apply_line_form_view').id,
                'target': 'new',
                'context': {
                    'default_form_id': self.form_id.id,
                    'default_apply_id': self._origin.id,
                    'default_form_line_id': self.form_id.question_ids[0].id
                },
            }


class FormApplyLine(models.Model):
    _name = 'form.apply.line'
    _description = 'Form Apply Line'
    _order = 'id'

    def save_and_close(self):
        return {'type': 'ir.actions.act_window_close'}

    def compute_has_next(self):
        for record in self:
            has_next = False
            ids = record.apply_id.apply_ids.mapped('id')
            ids.sort()
            if record._origin.id in ids:
                next_index = ids.index(record._origin.id) + 1
                if next_index < len(ids):
                    has_next = True
            record.has_next = has_next
    has_next = fields.Boolean(compute='compute_has_next')

    @api.onchange('form_line_id')
    def _onchange_form_line(self):
        for record in self:
            if record.form_line_id:
                record.name = record.form_line_id.title
                record.question_type = record.form_line_id.question_type

    @api.constrains('form_line_id')
    def constraint_form_line(self):
        for record in self:
            if record.form_line_id:
                record.name = record.form_line_id.title
                record.question_type = record.form_line_id.question_type

    @api.depends('form_line_id')
    @api.onchange('form_line_id')
    def compute_answer_lines(self):
        for record in self:
            answers = record.answers_ids
            if not record.answers_ids and record.form_line_id:
                line = record.form_line_id
                if line.question_type == 'matrix':
                    for m in line.suggested_answer_ids:
                        if line.matrix_answer_ids:
                            for c in line.matrix_answer_ids:
                                answers += record.answers_ids.create({
                                    'name': m.value,
                                    'val_name': c.value,

                                })
                        elif line.matrix_coltype == 'month':
                            num_days = monthrange(fields.date.today().year, fields.date.today().month)[1]
                            for c in range(1, num_days + 1):
                                answers += record.answers_ids.create({
                                    'name': m.value,
                                    'val_name': c,

                                })
                        elif line.matrix_coltype == 'week':
                            for c in range(0, 7):
                                answers += record.answers_ids.create({
                                    'name': m.value,
                                    'val_name': WeakDays[c],

                                })
            record.answers_ids = answers
            record.answers_text_ids = answers
            record.answers_date_ids = answers
            record.answers_datetime_ids = answers
            record.answers_char_ids = answers
            record.answers_v_ids = answers
    state = fields.Selection(related='apply_id.state', store=True)
    sequence = fields.Integer('Label Sequence order', default=10)
    name = fields.Char('Title', store=True, index=True)
    answer = fields.Char('Answer', compute='compute_answer')
    note = fields.Char('Note', store=True, index=True)
    text_char = fields.Char('Answer', store=True, index=True)
    text = fields.Text('Answer', store=True, index=True)
    numerical_box = fields.Float('Numerical', store=True, index=True)
    date = fields.Date('Date', store=True)
    check = fields.Boolean('Check', store=True, index=True)
    date_time = fields.Datetime('Date Time', store=True, index=True)
    form_line_id = fields.Many2one('form.design.line', 'Question', domain="[('form_id','=',form_id)]", store=True,
                                   index=True)
    form_id = fields.Many2one('form.design', 'Form', store=True, index=True)
    apply_id = fields.Many2one('form.apply', ondelete='cascade', index=True, store=True)
    employee_id = fields.Many2one('hr.employee', 'Responsible Employee', store=True)
    suggested_id = fields.Many2one('form.line.answer', 'Suggested Answer', domain="[('question_id','=',form_line_id)]",
                                   store=True)
    suggested_ids = fields.Many2many('form.line.answer', string='Suggested Answer',
                                     domain="[('question_id','=',form_line_id)]")
    answers_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', store=True,
                                  compute='compute_answer_lines')
    answers_v_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', store=True,
                                  compute='compute_answer_lines')
    answers_text_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', store=True,
                                       compute='compute_answer_lines')
    answers_date_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer',store=True,
                                       compute='compute_answer_lines')
    answers_datetime_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', store=True,
                                           compute='compute_answer_lines')
    answers_char_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer',store=True,
                                       compute='compute_answer_lines')
    question_type = fields.Selection([
        ('text_box', 'Multiple Lines Text Box'),
        ('char_box', 'Single Line Text Box'),
        ('numerical_box', 'Numerical Value'),
        ('check', 'True or False'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
        ('matrix', 'Matrix')], string='Question Type',
        readonly=False, store=True)
    matrix_answer_type = fields.Selection([('date', 'Date'),
                                           ('datetime', 'DateTime'),
                                           ('boolean', 'CheckBox'),
                                           ('numerical_box', 'Numerical Value'),
                                           ('char', 'Single Line Text Box'),
                                           ('text', 'Multiple Lines Text Box')], string='Matrix Answer Type',
                                          default='boolean', store=True)

    def confirm(self):
        ids = self.apply_id.apply_ids.mapped('id')
        ids.sort()
        if self._origin.id in ids:
            next_index = ids.index(self._origin.id) + 1
            if next_index < len(ids):
                return {
                    'name': _('Answers'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'form.apply.line',
                    'view_mode': 'form',
                    'view_id': self.env.ref('form_design.form_apply_line_form_view2').id,
                    'res_id': ids[next_index],
                    'target': 'new',
                    'context': self.env.context,
                }
            else:
                return {'type': 'ir.actions.act_window_close'}

    @api.onchange('text_char', 'text', 'check', 'numerical_box', 'date', 'date_time', 'suggested_id' 'suggested_ids',
                  'answers_ids')
    def compute_answer(self):
        for record in self:
            if record.question_type == 'char_box' and record.text_char:
                record.answer = record.text_char
            elif record.question_type == 'text_box' and record.text:
                record.answer = record.text
            elif record.question_type == 'check':
                record.answer = str(record.check)
            elif record.question_type == 'numerical_box' and record.numerical_box:
                record.answer = str(record.numerical_box)
            elif record.question_type == 'date' and record.date:
                record.answer = str(record.date)
            elif record.question_type == 'datetime' and record.date_time:
                record.answer = str(record.date_time)
            elif record.question_type == 'simple_choice' and record.suggested_id:
                record.answer = str(record.suggested_id.value)
            elif record.question_type == 'multiple_choice' and record.suggested_ids:
                record.answer = ','.join([r.value for r in record.suggested_ids])
            elif record.question_type == 'matrix' and record.answers_ids:
                if record.matrix_answer_type=='boolean':
                    record.answer = ','.join(
                        [r.name + ' ' + r.val_name for r in record.answers_ids.filtered(lambda x: x.check)])
                elif record.matrix_answer_type == 'text':
                    record.answer = ','.join(
                        [r.name + ' ' + r.val_name for r in record.answers_ids.filtered(lambda x: x.text)])
                elif record.matrix_answer_type == 'date':
                    record.answer = ','.join(
                        [r.name + ' ' + r.val_name for r in record.answers_ids.filtered(lambda x: x.date)])
                elif record.matrix_answer_type == 'datetime':
                    record.answer = ','.join(
                        [r.name + ' ' + r.val_name for r in record.answers_ids.filtered(lambda x: x.date_time)])
                elif record.matrix_answer_type == 'char':
                    record.answer = ','.join(
                        [r.name + ' ' + r.val_name for r in record.answers_ids.filtered(lambda x: x.textChar)])
            else:
                record.answer = False


class FormApplyLineMatrix(models.Model):
    _name = 'form.apply.line.matrix'
    _description = 'Form Apply Line Matrix'
    check = fields.Boolean('Check', store=True)
    value = fields.Float('Check', store=True)
    textChar = fields.Char('Answer', store=True)
    date = fields.Date('Answer', store=True)
    date_time = fields.Datetime('Answer', store=True)
    text = fields.Text('Answer', store=True)
    name = fields.Char('Row', store=True)
    val_name = fields.Char('Col', store=True)
    form_line_id = fields.Many2one('form.apply.line', 'Form Fill IN', ondelete='cascade', index=True)
