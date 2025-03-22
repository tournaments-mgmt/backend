import logging

import binascii
import magic

from odoo.api import Environment
from tournaments_backend.errors.services import NotFoundError

_logger = logging.getLogger(__name__)


def generate_image(odoo_field) -> dict:
    return {
        "imageData": odoo_field.decode(),
        "mimeType": magic.from_buffer(binascii.a2b_base64(odoo_field), mime=True),
    }


def generate_entrant(entrant) -> dict:
    return {
        "name": entrant.nickname,
        "color": entrant.avatar_color,
        "type": entrant.type,
    }


def generate_entrant_tournament_availability(entrant) -> dict:
    return {
        "name": entrant.entrant_id.nickname,
        "color": entrant.entrant_id.avatar_color,
        "type": entrant.entrant_id.type,
        "available": entrant.available,
    }


def generate_timestamp(odoo_field) -> dict | None:
    if not odoo_field:
        return None
    return odoo_field.timestamp() * 1000


def generate_matches(matches, result_config, show_incomplete_match=True) -> list[dict]:
    matches_list: list[dict] = list()
    result_config_match = result_config["match"]
    result_fields = result_config_match["result_fields_per_entrant"]
    player_per_game: int = len(result_fields)
    show_score_labels: bool = result_config_match["show_score_labels"]
    score_boolean: bool = result_config_match.get("score_boolean", False)
    scores_count: int = len(result_config_match["labels"])

    for match in matches:
        scores: list = list()
        entrants: list = [{}, {}]

        for match_entrant in match.match_entrant_ids:
            entrants[match_entrant.order_num] = generate_entrant(
                match_entrant.entrant_id
            )

        if not show_incomplete_match and len(entrants) < player_per_game:
            continue

        for match_entrant in match.match_entrant_ids:
            entrant_score: list = list()
            field_names: list[str] = result_fields[
                match.match_entrant_ids.ids.index(match_entrant.id)
            ]
            for match_result in match.match_result_ids:
                field_values: list = [
                    getattr(match_result, field_name) for field_name in field_names
                ]
                entrant_score.append(field_values)
            scores.append(entrant_score)

        winner = None
        if match.winner_match_entrant_id:
            winner = match.match_entrant_ids.ids.index(match.winner_match_entrant_id.id)

        matches_list.append(
            {
                "name": match.name,
                "phase": match.bracket_phase,
                "step": match.bracket_step,
                "num": match.bracket_num,
                "bestOf": int(match.best_of),
                "status": match.state,
                "scheduledStartTime": generate_timestamp(match.scheduled_start),
                "realStartTime": generate_timestamp(match.real_start),
                "scheduledEndTime": generate_timestamp(match.scheduled_end),
                "realEndTime": generate_timestamp(match.real_end),
                "entrants": entrants,
                "scoresLabels": result_config_match["labels"],
                "scoreBoolean": score_boolean,
                "scores": scores,
                "winner": winner,
                "entrantsCount": player_per_game,
                "scoresCount": scores_count,
                "showScoresLabels": show_score_labels,
            }
        )
    return matches_list


class PaneService:
    @staticmethod
    def get_next_showcase_pane_id(showcase_id: int, odoo_env: Environment) -> int:
        _logger.info(f"Asking for next pane id for showcase {showcase_id}")

        showcase_obj = odoo_env["tournaments.showcase"]
        showcase = showcase_obj.search([("id", "=", showcase_id)])
        if not showcase:
            raise NotFoundError(f"Showcase {showcase_id} not found")

        showcase.compute_next_showcase_pane_id()

        showcase_pane_id: int = showcase.next_showcase_pane_id.id

        return showcase_pane_id

    @staticmethod
    def get_pane_dict(pane_id: int, odoo_env: Environment) -> tuple[int, dict]:
        _logger.info(f"Getting data for showcase pane {pane_id}")

        showcase_pane_obj = odoo_env["tournaments.showcase.pane"]
        showcase_pane = showcase_pane_obj.search([("id", "=", pane_id)])
        if not showcase_pane:
            raise ValueError("Pane not found")

        duration: int = showcase_pane.pane_id.duration
        if showcase_pane.override_duration:
            duration = showcase_pane.duration

        pane_data: dict = {
            "duration": duration,
            "id": showcase_pane.pane_id.id,
            "name": showcase_pane.pane_id.name,
            "type": showcase_pane.pane_id.type_id.tag,
        }

        if showcase_pane.pane_id.type_id == odoo_env.ref(
            "showcases.data_tournaments_pane_type_text"
        ):
            pane_data["params"] = {
                "title": showcase_pane.pane_id.text_title,
                "subTitle": showcase_pane.pane_id.text_subtitle,
                "textMessage": showcase_pane.pane_id.text_message or "",
                "backgroundImage": generate_image(
                    showcase_pane.pane_id.text_background_file
                ),
            }

        elif showcase_pane.pane_id.type_id == odoo_env.ref(
            "showcases.data_tournaments_pane_type_image"
        ):
            pane_data["params"] = {
                "mimeType": showcase_pane.pane_id.image_file_mimetype,
                "imageData": showcase_pane.pane_id.image_file.decode(),
            }

        elif showcase_pane.pane_id.type_id == odoo_env.ref(
            "showcases.data_tournaments_pane_type_video"
        ):
            pane_data["params"] = {"videoUrl": showcase_pane.pane_id.video_url}

        elif showcase_pane.pane_id.type_id == odoo_env.ref(
            "showcases.data_tournaments_pane_type_tournament_entrants_list"
        ):
            tournament_entrant_obj = odoo_env["tournaments.tournament.entrant"]
            tournament = showcase_pane.pane_id.tournament_matches_tournament_id

            col_view: int = (
                showcase_pane.pane_id.tournament_classification_column_per_view or 4
            )
            item_col: int = (
                showcase_pane.pane_id.tournament_classification_items_per_column or 18
            )

            show_scheduled_time: bool = (
                showcase_pane.pane_id.tournament_matches_show_scheduled_time
            )

            entrants = tournament_entrant_obj.search(
                [
                    ("tournament_id", "=", tournament.id),
                ],
                order="entrant_nickname ASC",
            )
            pane_data["params"] = {
                "backgroundImage": generate_image(tournament.game_id.background_image),
                "platformImage": generate_image(tournament.platform_id.logo_image),
                "gameLogoImage": generate_image(tournament.game_id.logo_image),
                "name": showcase_pane.pane_id.display_name,
                "entrants": [
                    generate_entrant_tournament_availability(entrant)
                    for entrant in entrants
                ],
                "entrantsCount": len(tournament.entrant_ids),
                "itemsPerColumn": item_col,
                "columnPerView": col_view,
                "showScheduledTime": show_scheduled_time,
            }

        elif showcase_pane.pane_id.type_id == odoo_env.ref(
            "showcases.data_tournaments_pane_type_tournament_classification"
        ):
            match_obj = odoo_env["tournaments.match"]
            entrant_obj = odoo_env["tournaments.entrant"]

            tournament = showcase_pane.pane_id.tournament_matches_tournament_id

            game = tournament.game_id
            game_result_config: dict = game.result_config
            classification_config = game_result_config["classification"]

            col_view: int = (
                showcase_pane.pane_id.tournament_classification_column_per_view or 3
            )
            item_col: int = (
                showcase_pane.pane_id.tournament_classification_items_per_column or 15
            )

            show_scheduled_time: bool = (
                showcase_pane.pane_id.tournament_matches_show_scheduled_time
            )

            params: dict = {
                "name": tournament.name,
                "backgroundImage": generate_image(tournament.game_id.background_image),
                "platformImage": generate_image(tournament.platform_id.logo_image),
                "gameLogoImage": generate_image(tournament.game_id.logo_image),
                "resultsLabels": classification_config["labels"],
                "itemsPerColumn": item_col,
                "columnPerView": col_view,
                "showScheduledTime": show_scheduled_time,
            }

            entrant_ids: list[int] = [x.entrant_id.id for x in tournament.entrant_ids]
            entrants = entrant_obj.browse(entrant_ids)

            params_entrants: list[dict] = list()

            for entrant in entrants:
                match = match_obj.search(
                    [
                        ("tournament_id", "=", tournament.id),
                        ("match_entrant_ids.entrant_id", "=", entrant.id),
                        ("state", "in", ["done"]),
                    ],
                    order="real_start DESC",
                    limit=1,
                )
                if not match:
                    continue  # TODO: Verificare se il continue è corretto
                if not match.match_result_ids:
                    continue  # TODO: Verificare se il continue è corretto

                match_result = match.match_result_ids[0]

                params_entrants.append(
                    {
                        "name": entrant.nickname,
                        "color": entrant.avatar_color,
                        "type": entrant.type,
                        "results": [
                            getattr(match_result, field_name)
                            for field_name in classification_config["field_names"]
                        ],
                        "sort": [
                            getattr(match_result, field_name)
                            for field_name in classification_config["sort_field_names"]
                        ],
                        "position": 0,  # TODO: Compute position
                    }
                )

            params_entrants = sorted(
                params_entrants,
                key=lambda x: tuple(
                    x["sort"][pos] * direction
                    for pos, direction in classification_config["sort"]
                ),
                reverse=True,
            )

            for index, item in enumerate(params_entrants):
                params_entrants[index]["position"] = index + 1
                if 0 < index < len(params_entrants):
                    prev_item = params_entrants[index - 1]
                    if params_entrants[index]["results"] == prev_item["results"]:
                        params_entrants[index]["position"] = prev_item["position"]

            params["entrants"] = params_entrants
            pane_data["params"] = params

        elif showcase_pane.pane_id.type_id == odoo_env.ref(
            "showcases.data_tournaments_pane_type_tournament_best_of_matches"
        ) or showcase_pane.pane_id.type_id == odoo_env.ref(
            "showcases.data_tournaments_pane_type_tournament_single_matches"
        ):
            match_obj = odoo_env["tournaments.match"]
            tournament = showcase_pane.pane_id.tournament_matches_tournament_id
            game = tournament.game_id

            col_view: int = (
                showcase_pane.pane_id.tournament_classification_column_per_view or 3
            )
            item_col: int = (
                showcase_pane.pane_id.tournament_classification_items_per_column or 15
            )
            round: int = showcase_pane.pane_id.tournament_best_of_matches_round or 0
            result_config = game.result_config

            show_scheduled_time: bool = (
                showcase_pane.pane_id.tournament_matches_show_scheduled_time
            )

            params: dict = {
                "name": tournament.name,
                "backgroundImage": generate_image(tournament.game_id.background_image),
                "platformImage": generate_image(tournament.platform_id.logo_image),
                "gameLogoImage": generate_image(tournament.game_id.logo_image),
                "itemsPerColumn": item_col,
                "columnPerView": col_view,
                "showScheduledTime": show_scheduled_time,
            }

            matches = match_obj.search(
                [("tournament_id", "=", tournament.id), ("bracket_step", ">=", round)],
                order="bracket_step DESC, bracket_num ASC",
            )

            params_matches: list[dict] = generate_matches(
                matches, result_config, show_incomplete_match=False
            )

            params["matches"] = params_matches
            pane_data["params"] = params

        elif showcase_pane.pane_id.type_id == odoo_env.ref(
            "showcases.data_tournaments_pane_type_tournament_brackets"
        ):
            match_obj = odoo_env["tournaments.match"]

            tournament = showcase_pane.pane_id.tournament_matches_tournament_id
            game = tournament.game_id
            round: int = showcase_pane.pane_id.tournament_brackets_round or 3

            show_scheduled_time: bool = (
                showcase_pane.pane_id.tournament_matches_show_scheduled_time
            )

            result_config = game.result_config

            params: dict = {
                "name": tournament.name,
                "backgroundImage": generate_image(tournament.game_id.background_image),
                "platformImage": generate_image(tournament.platform_id.logo_image),
                "gameLogoImage": generate_image(tournament.game_id.logo_image),
                "round": round,
                "showScheduledTime": show_scheduled_time,
            }

            matches = match_obj.search(
                [("tournament_id", "=", tournament.id), ("bracket_step", "<=", round)],
                order="bracket_step DESC, bracket_num ASC",
            )

            params_matches: list[dict] = generate_matches(matches, result_config)

            params["matches"] = params_matches
            pane_data["params"] = params

        else:
            raise NotImplementedError

        return duration, pane_data
