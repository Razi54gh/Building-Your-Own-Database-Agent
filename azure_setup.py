"""Backward compatibility — gunakan llm_setup.py untuk provider baru."""

from llm_setup import (  # noqa: F401
    check_azure_config,
    check_llm_config,
    get_chat_model,
    get_deployment_name,
    get_model_name,
    get_openai_client,
    get_provider,
    print_provider_info,
    supports_assistants_api,
)
