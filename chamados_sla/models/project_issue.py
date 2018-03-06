# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

ALTA = '2'
MEDIA = '1'
BAIXA = '0'

PRIORITY_TABLE = {
    ALTA: {
        ALTA: (0.25, 4),
        MEDIA: (0.25, 4),
        BAIXA: (0.25, 8)
        },
    MEDIA: {
        ALTA: (0.25, 4),
        MEDIA: (0.25, 8),
        BAIXA: (1, 24)
        },
    BAIXA: {
        ALTA: (0.25, 8),
        MEDIA: (1, 24),
        BAIXA: (2, 36)
        }
    }


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    tempo_resposta = fields.Datetime(string=u"Prazo 1º Atend.",
                                     store=True,
                                     compute="_compute_tempo")
    tempo_resolucao = fields.Datetime(string=u"Prazo Solução",
                                      store=True,
                                      compute="_compute_tempo")
    tempo_excedido = fields.Boolean(string="Tempo Excedido",
                                    store=True,
                                    compute="_compute_excedido")

    impacto = fields.Selection(
        [('0', 'Baixo'), ('1', 'Médio'), ('2', 'Alto')],
        string="Impacto sobre negócios", oldname='x_impacto')

    @api.multi
    @api.depends("create_date", "priority", "impacto")
    def _compute_tempo(self):
        for item in self:
            if item.create_date and item.priority and item.impacto:
                valor = PRIORITY_TABLE[item.priority][item.impacto]
                data_python = fields.Datetime.from_string(item.create_date)
                calendar_id = item.project_id.resource_calendar_id
                item.tempo_resposta = calendar_id.plan_hours(
                    valor[0], data_python, compute_leaves=True)
                item.tempo_resolucao = calendar_id.plan_hours(
                    valor[1], data_python, compute_leaves=True)

    @api.multi
    def _compute_excedido(self):
        for item in self:
            result = False
            now = fields.Datetime.now()
            if item.stage_id.id not in [39, 40, 41, 62, 46, 47] \
               and now > item.tempo_resposta \
               and item.stage_id.sequence <= 10:
                result = True
            if item.stage_id.id not in [40, 41, 62, 46, 47] \
               and now > item.tempo_resolucao \
               and item.stage_id.sequence <= 100:
                result = True
            item.tempo_excedido = result