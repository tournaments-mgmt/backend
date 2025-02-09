import logging
import numbers

from odoo import models, fields, api
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class Match(models.Model):
    _name = "tournaments.match"
    _description = "Match"
    _order = "order_num, scheduled_start"

    _inherit = [
        "tournaments.scheduled",
        "tournaments.extid",
        "mail.thread",
        "mail.activity.mixin"
    ]

    name = fields.Char(
        string="Name",
        help="Name",
        compute="_compute_name",
        copy=False,
        tracking=True,
        store=True
    )

    tournament_id = fields.Many2one(
        string="Tournament",
        help="Related tournament",
        comodel_name="tournaments.tournament",
        required=True,
        readonly=True
    )

    tournament_type = fields.Selection(
        related="tournament_id.type",
        store=True
    )

    order_num = fields.Integer(
        string="Order",
        help="Order number",
        required=True,
        default=0
    )

    scheduled_start = fields.Datetime(
        required=False
    )

    game_id = fields.Many2one(
        string="Game",
        related="tournament_id.game_id",
        store=True
    )

    game_logo_image = fields.Image(
        string="Game Logo",
        related="game_id.logo_image"
    )

    game_pegi_age_logo = fields.Image(
        string="Game Tournament PEGI Age Label",
        related="game_id.pegi_age_id.logo"
    )

    platform_id = fields.Many2one(
        string="Platform",
        related="tournament_id.platform_id",
        store=True
    )

    platform_logo_image = fields.Image(
        string="Platform Logo",
        related="platform_id.logo_image"
    )

    # match_entrant_ids = fields.One2many(
    #     string="Entrants",
    #     help="Entrant players",
    #     comodel_name="tournaments.match.entrant",
    #     inverse_name="match_id",
    #     domain="[('tournament_entrant_id.tournament_id', '=', tournament_id)]",
    #     copy=False,
    #     tracking=True,
    # )

    # match_entrant_count = fields.Integer(
    #     string="Entrants count",
    #     help="Entrant players count",
    #     compute="_compute_match_entrant_count",
    #     store=True
    # )

    bracket_step = fields.Integer(
        string="Step",
        help="Step in bracket",
        readonly=True
    )

    bracket_phase = fields.Integer(
        string="Phase",
        help="Phase of the bracket",
        readonly=True
    )

    bracket_phase_name = fields.Char(
        string="Bracket Phase",
        help="Bracket Phase",
        compute="_compute_bracket_phase_name"
    )

    bracket_num = fields.Integer(
        string="Num",
        help="Progressive number in phase",
        readonly=True
    )

    # match_result_ids = fields.One2many(
    #     string="Results",
    #     help="Match Results",
    #     comodel_name="tournaments.match.result",
    #     inverse_name="match_id"
    # )
    #
    # winner_match_entrant_id = fields.Many2one(
    #     string="Winner Match Entrant",
    #     help="Winner Match Entrant",
    #     comodel_name="tournaments.match.entrant",
    #     domain="[('id', 'in', match_entrant_ids)]",
    #     tracking=True
    # )

    @api.model_create_multi
    @api.returns("self", lambda value: value.id)
    def create(self, vals_list):
        ret = super().create(vals_list)

        if ret.tournament_id.scheduled_state in ["done", "canceled"]:
            ret.tournament_id.scheduled_state = "running"

        return ret

    # def write(self, vals):
    #     ret = super().write(vals)
    #     for rec in self:
    #         if rec.tournament_type_id.id != self.env.ref("tournaments.data_tournaments_tournament_type_bracket").id:
    #             continue
    #         if "state" not in vals or vals["state"] != "done":
    #             continue
    #         rec.bracket_forward_winners()
    #     return ret

    def unlink(self):
        tournament_obj = self.env["tournaments.tournament"]

        tournament_ids = [rec.tournament_id.id for rec in self]
        ret = super().unlink()
        tournament_obj.browse(tournament_ids).update_state()
        return ret

    # @api.depends("match_entrant_ids")
    # def _compute_match_entrant_count(self):
    #     for rec in self:
    #         rec.match_entrant_count = len(rec.match_entrant_ids)

    # @api.depends("match_entrant_ids")
    def _compute_name(self):
        for rec in self:
            if not rec.tournament_id:
                rec.name = False

            items: list[str] = [
                rec.tournament_id.name_get()[0][1]
            ]

            if rec.tournament_id.type == "bracket":
                items.append(rec.bracket_phase_name)

            entrant_items: list[str] = [x.name_get()[0][1] for x in rec.match_entrant_ids.tournament_entrant_id]
            if not entrant_items:
                entrant_items = [f"{rec.bracket_num}"]

            items.append(" VS ".join(entrant_items))
            rec.name = " - ".join(items)

    @api.depends("bracket_phase")
    def _compute_bracket_phase_name(self):
        for rec in self:
            if rec.bracket_phase <= 1:
                final_matches_count = self.search_count([
                    ("tournament_id", "=", rec.tournament_id.id),
                    ("bracket_step", "=", 0)
                ])
                if final_matches_count > 1 and rec.bracket_num == 0:
                    bracket_phase_name = _("Final 3rd4th")
                else:
                    bracket_phase_name = _("Final")

                rec.bracket_phase_name = bracket_phase_name
            elif rec.bracket_phase <= 2:
                rec.bracket_phase_name = _("Semi-finals")
            elif rec.bracket_phase <= 4:
                rec.bracket_phase_name = _("Quarter-finals")
            elif rec.bracket_phase <= 8:
                rec.bracket_phase_name = _("Eighth-finals")
            else:
                rec.bracket_phase_name = _("%s-finals") % numbers.ordinal(rec.bracket_phase)

    def action_start(self, propagate: bool = True):
        # for rec in self:
        #     if not rec.match_entrant_ids:
        #         raise ValidationError(_("Unable to start match. There are no entrants."))

        super().action_start(propagate)
        if propagate:
            self.tournament_id.update_state()

    def action_end(self, propagate: bool = True):
        super().action_end(propagate)
        if propagate:
            self.tournament_id.update_state()

    def action_cancel(self, propagate: bool = True):
        super().action_cancel(propagate)
        if propagate:
            self.tournament_id.update_state()

    def action_reset(self, propagate: bool = True):
        super().action_reset(propagate)
        if propagate:
            self.tournament_id.update_state()

    # def quick_win(self):
    #     for rec in self:
    #         rec.ensure_one()
    #
    #         if len(rec.match_entrant_ids) != 1:
    #             raise ValidationError(
    #                 _("Match has no entrant or multiple entrants. Quick win is possible with only one entrant."))
    #
    #         rec.winner_match_entrant_id = rec.match_entrant_ids[0].id
    #         rec.state_start()
    #         rec.state_end()

    # def action_add_match_result(self):
    #     self.ensure_one()
    #
    #     context = dict(self.env.context)
    #     context.update({
    #         "default_match_id": self.id
    #     })
    #
    #     return {
    #         "type": "ir.actions.act_window",
    #         "name": _("Adds Match Result"),
    #         "res_model": "tournaments.wizard.match.result",
    #         "view_mode": "form",
    #         "target": "new",
    #         "context": context
    #     }

    # def bracket_forward_winners(self):
    #     for rec in self:
    #         if rec.state not in ["canceled"] and not rec.winner_match_entrant_id:
    #             _logger.warning("No winner set in this match")
    #             continue
    #
    #         next_step_match_num = int(rec.bracket_num / 2)
    #         group_first_match_num: int = next_step_match_num * 2
    #
    #         sibling_match = self.search([
    #             ("tournament_id", "=", rec.tournament_id.id),
    #             ("bracket_step", "=", rec.bracket_step),
    #             ("bracket_num", "in", [group_first_match_num, group_first_match_num + 1]),
    #             ("bracket_num", "!=", rec.bracket_num)
    #         ])
    #         if len(sibling_match) != 1:
    #             _logger.warning("Unable to find sibling match")
    #             continue
    #
    #         # if sibling_match.state not in ["canceled"] and not sibling_match.winner_match_entrant_id:
    #         #     _logger.warning("Sibling match has no winner yet")
    #         #     continue
    #
    #         if rec.bracket_step == 1:
    #             next_step_match = self.search([
    #                 ("tournament_id", "=", rec.tournament_id.id),
    #                 ("bracket_step", "=", 0)
    #             ], order="bracket_num DESC", limit=1)
    #         else:
    #             next_step_match = self.search([
    #                 ("tournament_id", "=", rec.tournament_id.id),
    #                 ("bracket_step", "=", rec.bracket_step - 1),
    #                 ("bracket_num", "=", next_step_match_num)
    #             ])
    #
    #         if len(next_step_match) != 1:
    #             _logger.warning("Unable to find next-step match")
    #             continue
    #
    #         if len(next_step_match.match_entrant_ids) > 1:
    #             _logger.warning("Next-step match has entrant already defined")
    #             continue
    #
    #         # a_match_entrant = None
    #         # b_match_entrant = None
    #         # if self.bracket_num > sibling_match.bracket_num:
    #         #     b_match_entrant = self.winner_match_entrant_id
    #         #     if sibling_match.winner_match_entrant_id:
    #         #         a_match_entrant = sibling_match.winner_match_entrant_id
    #         # else:
    #         #     a_match_entrant = self.winner_match_entrant_id
    #         #     if sibling_match.winner_match_entrant_id:
    #         #         b_match_entrant = sibling_match.winner_match_entrant_id
    #         #
    #         # if not a_match_entrant and not b_match_entrant:
    #         #     next_step_match.state_cancel()
    #         #     continue
    #
    #         match_entrant_ids: list = list()
    #
    #         if rec.bracket_num % 2 == 0:
    #             a_match_entrant = self.winner_match_entrant_id
    #             match_entrant_ids.append((0, 0, {
    #                 "match_id": next_step_match.id,
    #                 "tournament_entrant_id": a_match_entrant.tournament_entrant_id.id,
    #                 "order_num": 0
    #             }))
    #         else:
    #             b_match_entrant = self.winner_match_entrant_id
    #             match_entrant_ids.append((0, 0, {
    #                 "match_id": next_step_match.id,
    #                 "tournament_entrant_id": b_match_entrant.tournament_entrant_id.id,
    #                 "order_num": 1
    #             }))
    #
    #         # if a_match_entrant:
    #         #     if a_match_entrant not in next_step_match.match_entrant_ids:
    #         #         match_entrant_ids. append((0, 0, {
    #         #             "match_id": next_step_match.id,
    #         #             "tournament_entrant_id": a_match_entrant.tournament_entrant_id.id,
    #         #             "order_num": 0
    #         #         }))
    #         #
    #         # if b_match_entrant:
    #         #     if b_match_entrant not in next_step_match.match_entrant_ids:
    #         #         match_entrant_ids.append((0, 0, {
    #         #             "match_id": next_step_match.id,
    #         #             "tournament_entrant_id": b_match_entrant.tournament_entrant_id.id,
    #         #             "order_num": 1
    #         #         }))
    #
    #         next_step_match.write({
    #             "match_entrant_ids": match_entrant_ids
    #         })

    # def manual_set_state(self):
    #     self.ensure_one()
    #
    #     context = dict(self.env.context)
    #     context.update({
    #         "default_match_id": self.id
    #     })
    #
    #     return {
    #         "type": "ir.actions.act_window",
    #         "name": _("Manual set Match State"),
    #         "res_model": "tournaments.wizard.match.state.manualset",
    #         "view_mode": "form",
    #         "target": "new",
    #         "context": context
    #     }

    # def compute_winner(self):
    #     self.ensure_one()
