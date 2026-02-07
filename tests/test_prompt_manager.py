# -*- coding: utf-8 -*-
"""Tests para prompt_manager."""
import pytest

from modules.prompt_manager import (
    get_prompt,
    render_prompt,
    load_template,
    get_available_templates,
    DEFAULT_PROMPT,
    TEMPLATE_MAP,
)


class TestGetPrompt:
    def test_default_prompt_returned(self):
        result = get_prompt()
        assert result == DEFAULT_PROMPT

    def test_custom_prompt_takes_precedence(self):
        custom = "Mi prompt personalizado con {client_name}"
        result = get_prompt(custom_prompt=custom)
        assert result == custom

    def test_empty_custom_falls_to_default(self):
        result = get_prompt(custom_prompt="   ")
        assert result == DEFAULT_PROMPT

    def test_specialized_template_loaded(self):
        result = get_prompt(report_type="Ventas y KPIs")
        assert "VENTAS" in result.upper() or "COMERCIAL" in result.upper()
        assert result != DEFAULT_PROMPT

    def test_general_type_returns_default(self):
        result = get_prompt(report_type="Análisis General")
        assert result == DEFAULT_PROMPT

    def test_personalizado_returns_default(self):
        result = get_prompt(report_type="Personalizado")
        assert result == DEFAULT_PROMPT

    def test_custom_overrides_report_type(self):
        custom = "Override prompt"
        result = get_prompt(custom_prompt=custom, report_type="Ventas y KPIs")
        assert result == custom


class TestLoadTemplate:
    def test_known_types_load(self):
        for report_type in TEMPLATE_MAP:
            template = load_template(report_type)
            assert len(template) > 100
            assert "{client_name}" in template
            assert "{data_summary}" in template

    def test_unknown_type_returns_default(self):
        result = load_template("Tipo Inexistente")
        assert result == DEFAULT_PROMPT


class TestRenderPrompt:
    def test_variables_substituted(self):
        template = "Cliente: {client_name}, Periodo: {period}, Tipo: {report_type}"
        result = render_prompt(
            template=template,
            client_name="Acme",
            period="Enero 2025",
            report_type="General",
            total_records=100,
            data_summary="datos...",
            quantitative_analysis="análisis...",
        )
        assert "Acme" in result
        assert "Enero 2025" in result
        assert "{client_name}" not in result


class TestAvailableTemplates:
    def test_returns_dict(self):
        available = get_available_templates()
        assert isinstance(available, dict)
        assert len(available) > 0

    def test_all_mapped_types_available(self):
        available = get_available_templates()
        for report_type in TEMPLATE_MAP:
            assert report_type in available
