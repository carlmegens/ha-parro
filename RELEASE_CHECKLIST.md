# Releasecontrole

## Voor iedere release

1. Voer de volledige workflow **Validate** uit op de commit die wordt gepubliceerd: HACS-validatie zonder overgeslagen controles, Hassfest, Python-regressietests en browsertests.
2. Controleer `scripts/prepare_repository.py --check` en bouw een nieuwe installatie-ZIP. De distributielijst bevat alleen de integratie, openbare documentatie en generieke voorbeelden.
3. Controleer de verschillen op onbedoelde schoolinhoud, tokens, privé-abonnementslinks, screenshots en lokale overdrachtsbestanden.
4. Maak pas na een volledig geslaagde workflow de GitHub-release. Leg commit, controlelink, wijzigingen en beperkingen vast in de releasenotities.
5. Werk een bestaande installatie bij, herstart Home Assistant en controleer de geladen integratie en logboeken.
6. Controleer bij agenda-aanpassingen de native agenda-entiteit en `calendar.get_events`, hele dagen, tijdzones, herhaling, fouten en herstel. Vergelijk waar mogelijk met Parro zonder schoolinhoud in openbare verslagen op te nemen.
7. Bij een catalogusaanvraag: link de nieuwe release en de geslaagde HACS- en Hassfest-taken. Een ingediende aanvraag is nog geen opname in de Marketplace.

## Automatische dekking vanaf 0.4.0

- Python-tests op Home Assistant 2026.8.3 met `ical` 14.1.1 en 2026.10.4 met `ical` 14.3.1.
- Synthetische tests voor aanmelding, tokens, rechten, mededelingen, gesprekken, foto's, agenda, afsluiten en distributie.
- Browsertests met de echte kaart en apparaatpop-ups, uitsluitend met verzonnen inhoud.
- HACS-validatie en Hassfest bij wijzigingen, versietags, handmatige start en wekelijks.

Het beschikbare testpakket ondersteunt Home Assistant 2026.11 nog niet volledig. De volledige regressiesuite draait daarom op de twee bovenstaande versies. Kalenderverwerking is afzonderlijk op 2026.11 gecontroleerd; de praktijkcontrole en definitieve workflowresultaten staan in de release-informatie. Tests met verzonnen gegevens garanderen geen volledigheid van de Parro-agenda of berichtenhistorie voor ieder account.
