"""Vigipool integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF_TOPIC_PREFIX, DOMAIN
from .coordinator import VigipoolCoordinator
from .schedule import DAY_SWITCHES

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
    Platform.LIGHT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vigipool from a config entry."""
    await _async_cleanup_obsolete_entities(hass, entry)

    coordinator = VigipoolCoordinator(hass, entry)
    await coordinator.async_start()

    unload_listener = entry.add_update_listener(async_reload_entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "unload_listener": unload_listener,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        data["unload_listener"]()
        coordinator: VigipoolCoordinator = data["coordinator"]
        await coordinator.async_stop()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_cleanup_obsolete_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Remove legacy schedule entities replaced by the compact editor."""
    registry = er.async_get(hass)
    topic_prefix = entry.options.get(CONF_TOPIC_PREFIX, entry.data[CONF_TOPIC_PREFIX])

    obsolete_suffixes = {
        f"filter_program_{program_index + 1}_{day_key}"
        for program_index in range(2)
        for _, day_key, _ in DAY_SWITCHES
    }
    obsolete_suffixes.update(
        {
            f"filter_program_{program_index + 1}_slot_{slot_index + 1}_{boundary}"
            for program_index in range(2)
            for slot_index in range(3)
            for boundary in ("start", "end", "clear")
        }
    )

    for entity_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        unique_id = entity_entry.unique_id
        if unique_id in {
            f"{topic_prefix}_{suffix}"
            for suffix in obsolete_suffixes
        }:
            registry.async_remove(entity_entry.entity_id)
