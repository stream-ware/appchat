from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("streamware.workflow")

APPS_DIR = Path(__file__).parent.parent / "apps"

_WORKFLOW_CACHE: Dict[str, Optional[Any]] = {}


def _load_workflow_module(app_id: str) -> Optional[Any]:
    if not app_id:
        return None

    cached = _WORKFLOW_CACHE.get(app_id)
    if app_id in _WORKFLOW_CACHE:
        return cached

    workflow_path = APPS_DIR / app_id / "workflow.py"
    if not workflow_path.exists():
        _WORKFLOW_CACHE[app_id] = None
        return None

    module_name = f"streamware.apps.{app_id}.workflow"

    try:
        spec = importlib.util.spec_from_file_location(module_name, workflow_path)
        if spec is None or spec.loader is None:
            _WORKFLOW_CACHE[app_id] = None
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _WORKFLOW_CACHE[app_id] = module
        return module
    except Exception as exc:
        logger.warning("Failed to load workflow for %s: %s", app_id, exc)
        _WORKFLOW_CACHE[app_id] = None
        return None


def resolve_active_app(session_id: Optional[str], session_manager: Any, context_manager: Any) -> Optional[str]:
    if session_id and session_manager and hasattr(session_manager, "get_session"):
        try:
            session = session_manager.get_session(session_id)
        except Exception:
            session = None

        if isinstance(session, dict):
            current_app = session.get("current_app")
            if current_app and current_app != "system":
                return current_app

    if session_id and context_manager and hasattr(context_manager, "get_or_create_session"):
        try:
            ctx_session = context_manager.get_or_create_session(session_id)
        except Exception:
            ctx_session = None

        app_states = getattr(ctx_session, "app_states", None)
        if isinstance(app_states, dict) and app_states:
            latest_state = None
            for state in app_states.values():
                app_id = getattr(state, "app_id", None)
                if not app_id or app_id == "system":
                    continue
                if latest_state is None:
                    latest_state = state
                    continue
                if str(getattr(state, "timestamp", "")) > str(getattr(latest_state, "timestamp", "")):
                    latest_state = state

            if latest_state is not None:
                app_id = getattr(latest_state, "app_id", None)
                if app_id:
                    return app_id

    return None


def apply_app_workflow(
    *,
    session_id: Optional[str],
    command: str,
    intent: Dict[str, Any],
    session_manager: Any,
    context_manager: Any,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not isinstance(intent, dict):
        return intent

    command = command or ""
    extra = extra or {}

    if intent.get("recognized"):
        app_id = intent.get("app_type")
        module = _load_workflow_module(str(app_id or ""))
        if not module:
            return intent

        last_result = None
        if session_id and context_manager and hasattr(context_manager, "get_last_app_result"):
            try:
                last_result = context_manager.get_last_app_result(session_id, app_id)
            except Exception:
                last_result = None

        preprocess = getattr(module, "preprocess_intent", None)
        if callable(preprocess):
            try:
                updated = preprocess(intent=intent, last_result=last_result, command=command, extra=extra)
                if isinstance(updated, dict):
                    return updated
            except Exception as exc:
                logger.warning("Workflow preprocess failed for %s: %s", app_id, exc)

        return intent

    active_app = resolve_active_app(session_id, session_manager, context_manager)
    if not active_app:
        return intent

    updated_intent = dict(intent)
    updated_intent["active_app"] = active_app

    module = _load_workflow_module(active_app)
    if not module:
        return updated_intent

    last_result = None
    if session_id and context_manager and hasattr(context_manager, "get_last_app_result"):
        try:
            last_result = context_manager.get_last_app_result(session_id, active_app)
        except Exception:
            last_result = None

    route_followup = getattr(module, "route_followup", None)
    if callable(route_followup):
        try:
            routed = route_followup(command=command, last_result=last_result, extra=extra)
        except Exception as exc:
            logger.warning("Workflow route_followup failed for %s: %s", active_app, exc)
            routed = None

        if isinstance(routed, dict) and routed.get("recognized"):
            routed.setdefault("original_command", command)
            routed.setdefault("params", {})
            routed.setdefault("confidence", 0.6)
            routed["workflow_routed"] = True
            routed["workflow_app"] = active_app

            preprocess = getattr(module, "preprocess_intent", None)
            if callable(preprocess):
                try:
                    updated = preprocess(intent=routed, last_result=last_result, command=command, extra=extra)
                    if isinstance(updated, dict):
                        routed = updated
                except Exception as exc:
                    logger.warning("Workflow preprocess failed for %s: %s", active_app, exc)

            return routed

    return updated_intent
