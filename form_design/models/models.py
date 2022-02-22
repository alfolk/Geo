from odoo import models, fields, _


WeakDays = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


class FormDesign(models.Model):
    _name = 'form.design'
    _description = 'Form Design'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def compute_form_fill_in(self):
        for record in self:
            record.fill_count = len(record.form_ids)
    category = fields.Many2one('alfolk.partner.category','Partner Category', store=True)
    name = fields.Char('Form Title', required=True, translate=True, tracking=True, store=True, index=True, )
    color = fields.Integer('Color Index', default=0)
    fill_count = fields.Integer('Form Fill In count', default=0, compute='compute_form_fill_in')
    form_ids = fields.One2many('form.apply', 'form_id', 'Form Fill In')
    description = fields.Html(
        "Description", sanitize=False, translate=True, tracking=True, store=True, index=True, )
    description_done = fields.Html(
        "End Message", translate=True,
        help="This message will be displayed when survey is completed")
    active = fields.Boolean("Active", default=True)
    allow_add = fields.Boolean("Allow Add Line", default=False)
    res_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True,
                             store=True, index=True)
    question_ids = fields.One2many('form.design.line', 'form_id', tracking=True, store=True, index=True, translate=True)

    def view_form_fill_in(self):
        return {
            'name': _(f'Filled out forms of {self.name}'),
            'type': 'ir.actions.act_window',
            'res_model': 'form.apply',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.form_ids.ids)],
            'context': "{'default_form_id': " + str(self._origin.id) + "}",
        }

    def form_fill_in(self):
        lines = []
        for line in self.question_ids:
            lines.append((0, 0, {
                'name': line.title,
                'sequence': line.sequence,
                'form_line_id': line.id,
                'form_id': self._origin.id,
                'question_type': line.question_type,
                'matrix_answer_type': line.matrix_answer_type,
            }))
        return {
            'name': _('Form Fill Out'),
            'type': 'ir.actions.act_window',
            'res_model': 'form.apply',
            'view_mode': 'form',
            'view_id': self.env.ref('form_design.form_apply_form_view').id,
            'target': 'new',
            'context': {
                'default_form_id': self._origin.id,
                'default_apply_ids': lines,
            },
        }


class FormDesignLine(models.Model):
    _name = 'form.design.line'
    _description = 'Form Design Line'
    _rec_name = "title"
    title = fields.Char('Title', required=True, translate=True, tracking=True, store=True, index=True)
    description = fields.Html(
        'Description', translate=True, sanitize=False,
        help="Use this field to add additional explanations about your " +
             "question or to illustrate it with pictures or a video")

    form_id = fields.Many2one('form.design', string='Form', ondelete='cascade', tracking=True, store=True, index=True)
    sequence = fields.Integer('Sequence', default=10, tracking=True, store=True, index=True)
    question_type = fields.Selection([
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('check', 'CheckBox'),
        ('numerical_box', 'Numerical Value'),
        ('text_box', 'Multiple Lines Text Box'),
        ('char_box', 'Single Line Text Box'),
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
        ('matrix', 'Matrix')], string='Question Type',
        readonly=False, store=True, tracking=True, index=True)
    matrix_subtype = fields.Selection([
        ('simple', 'One choice per row'),
        ('multiple', 'Multiple choices per row')], string='Matrix Type', default='simple')
    column_nb = fields.Selection([
        ('12', '1'), ('6', '2'), ('4', '3'), ('3', '4'), ('2', '6')],
        string='Number of columns', default='12',
        help='These options refer to col-xx-[12|6|4|3|2] classes in Bootstrap for dropdown-based simple and multiple '
             'choice questions.')
    suggested_answer_ids = fields.One2many('form.line.answer', 'question_id', 'Answers')
    matrix_answer_type = fields.Selection([('date', 'Date'),
                                           ('datetime', 'DateTime'),
                                           ('boolean', 'CheckBox'),
                                           ('numerical_box', 'Numerical Value'),
                                           ('char', 'Single Line Text Box'),
                                           ('text', 'Multiple Lines Text Box')], string='Matrix Answer Type',
                                          default='boolean', store=True)
    matrix_answer_ids = fields.One2many('form.line.answer', 'matrix_question_id', 'Answers', copy=True)
    matrix_coltype = fields.Selection([
        ('custom', 'Custom'),
        ('week', 'Days of the Week'),
        ('month', 'Days of the Month'),

    ], string='Matrix Columns', default='custom')


class SurveyQuestionAnswer(models.Model):
    _name = 'form.line.answer'
    _description = 'Answers'
    _rec_name = "value"
    _order = 'sequence'
    question_id = fields.Many2one('form.design.line', string='Question', ondelete='cascade')
    matrix_question_id = fields.Many2one('form.design.line', string='Question (as matrix row)', ondelete='cascade')
    sequence = fields.Integer('Label Sequence order', default=10)
    value = fields.Char('Suggested value', translate=True, required=True)
    is_correct = fields.Boolean('Is a correct answer')
