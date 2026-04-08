# 0.1.1

Small quality-of-life update for the first Vigipool release.

## Included in this version

- added human-readable state entities for the most visible Vigipool codes
- moved several raw code sensors into the diagnostic category
- kept the original numeric values available through attributes for debugging

## Main user-facing changes

- new readable `Filter state` entity
- new readable `Aux mode` entity
- new readable `Action` entity
- new readable `Frost free status` entity

## Notes

This is still a read-only MQTT integration.

MQTT writes for filtration, lighting and auxiliary control will come in the next iteration once the writable topics are confirmed cleanly.
