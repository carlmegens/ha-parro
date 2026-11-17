# Wijzigingen

## 1.1.0b2 — 2026-11-17 (pre-release)

- Uses the supplied project icon, exported from the Illustrator artwork at 256 and 512 pixels with transparency.
- Shows the project icon in the README and clarifies attribution for the modified brand illustration.
- Branding-only update; functionality is unchanged from 1.1.0b1. Version 1.0.0 remains the stable release.

## 1.1.0b1 — 2026-11-17 (pre-release)

This is an opt-in test release. New features have synthetic integration tests but have not yet been validated against a real school account. The stable release remains 1.0.0.

- Opt-in child devices with a group sensor, native child calendar and profile photo.
- Six opt-in native image slots for recent announcement photos.
- Minimal event entities and automation events for newly observed announcements and chat activity; silent startup baseline.
- Administrator/automation reply action, disabled by default, with explicit room allowlist, server-side room policy checks and durable attempt limits. No automatic delivery retries.
- Exclude calendar text attributes from new Recorder storage.
- Document shared-entity visibility, message delivery limitations, third-party attribution and trademarks.
- Existing account entities, read actions and dashboard configuration remain compatible.

## 1.0.0 — eerste stabiele release

- Markeert de bestaande functionaliteit van 0.4.3 als stabiele basis: mededelingen, gesprekken, beschikbare foto’s, schoolagenda, apparaat-pop-ups en optionele dashboardkaart.
- Legt de compatibiliteitsafspraak voor entiteit-identiteiten, gedocumenteerde acties, API-antwoorden en kaartinstellingen vast in de README.
- Behoudt de bestaande configuratie, entiteiten, toegangsrechten en frontend. Bijwerken vanuit 0.4.3 vereist geen nieuwe aanmelding of migratie; Home Assistant herstarten volstaat.
- Bevat de installatie-instructies voor de goedgekeurde Marketplace-/HACS-catalogus. De bestaande functionele beperkingen blijven gedocumenteerd.

## 0.4.3 — Agenda-tab in het Parro-scherm

- Voegt Agenda toe naast Mededelingen en Gesprekken, met de bestaande lijst van komende schoolafspraken, vernieuwen en een link naar de volledige agenda.
- Koppelt de lijst aan de schoolagenda van het gekozen account, onafhankelijk van toegang tot mededelingen en gesprekken; de normale Home Assistant-agendarechten blijven gelden.
- Wist geladen en nog onderweg zijnde inhoud bij wisselen van account, tab of gebruiker en bij sluiten; volgt hernoemde of verwijderde kalenderentiteiten.

## 0.4.2 — komende afspraken in de apparaatpop-up

- Hernoemt de GitHub-repository naar `carlmegens/ha-parro` op verzoek van de catalogusreview. De integratienaam en entiteit-ID’s blijven gelijk; bestaande GitHub-links worden doorgestuurd.

- Klik op **Volgende schoolafspraak** voor maximaal 20 komende of lopende afspraken binnen 365 dagen, met datum, tijd, locatie en hele-dag-aanduiding.
- Opent de volledige Agenda vanuit de lijst en biedt vernieuwen, laden, leeg en opnieuw proberen.
- Gebruikt de bestaande agenda en Home Assistant-entiteitsrechten; de lijst wordt niet als sensorattribuut opgeslagen. Volgt hernoemde agenda-entiteiten en wist geladen inhoud bij wisselen van gebruiker of sluiten van de pop-up.
- Vernieuwt de meegeleverde frontendversie. Herlaad na installatie zo nodig eenmaal de browser.

## 0.4.1 — volgende schoolafspraak

- Voegt **Volgende schoolafspraak** toe aan het bestaande Parro-apparaat: datum en tijd, met titel, locatie, eindtijd en hele-dag-aanduiding in de details.
- Laat begonnen afspraken binnen een minuut doorschuiven naar de volgende. De sensor deelt de bestaande agendacache en veroorzaakt geen extra abonnementsdownloads.
- Behoudt de native kalenderentiteit, entiteit-ID en kalenderautomatiseringen. Verduidelijkt de betekenis van de standaard Aan/Uit-status in de README.

## 0.4.0 — schoolagenda en automatische releasecontroles

- Voegt een native, alleen-lezen schoolagenda toe aan het Parro-apparaat, de Home Assistant-agenda en standaard agendakaarten en automatiseringen.
- Leest accountabonnementen automatisch en verwerkt hele dagen, tijdzones, herhaling, uitzonderingen en geannuleerde afspraken.
- Houdt abonnementslinks privé en begrenst downloads en agenda-aanvragen. De schoolagenda gebruikt de normale Home Assistant-entiteitsrechten; de aparte Parro-berichtrechten gelden niet voor agenda-inhoud.
- Voegt GitHub Actions toe voor HACS, Hassfest, Python-tests op twee Home Assistant-versies en de bestaande browsertests.

## 0.3.1 — Parro-logo

- Vervangt het tijdelijke blauwe P-pictogram door het aangeleverde kleurrijke Parro-logo. De transparante afbeelding wordt lokaal met de integratie meegeleverd.
- Geen wijzigingen aan aanmelding, sensoren, berichten, foto’s of toegangsrechten.

## 0.3.0 — lezen vanuit het Parro-apparaat

- De bestaande tellers **Ongelezen mededelingen** en **Ongelezen gesprekken** openen de passende Parro-pop-up. Er zijn geen extra entiteiten of een afzonderlijk dashboard nodig.
- Voegt een interne apparaatlink naar hetzelfde meegeleverde Parro-scherm toe. De weergave wordt globaal geladen, zodat direct openen vanaf de apparaatpagina werkt; de bestaande integratieopties blijven bereikbaar.
- Toont een begrensde gesprekkenlijst en berichten uit een gekozen gesprek. Toegang voor andere Home Assistant-gebruikers is apart instelbaar; bestaande toegang tot mededelingen verleent geen gespreksrechten.
- Gebruikt voor berichtinhoud en beschikbare foto's de geauthenticeerde routes. Sensorattributen bevatten alleen niet-gevoelige verwijzingen naar de pop-up en het account, zonder berichtinhoud, foto's of toegangstokens.
- Behoudt de dashboardkaart als optionele weergave in hetzelfde installatiepakket.

Lokaal gecontroleerd met 482 Python-tests tegen Home Assistant Core 2026.8.3. De [releasechecklist](RELEASE_CHECKLIST.md) scheidt lokale controles van de praktijkproef.

Gespreksfoto’s volgen het `attachment`-veld van `RChatTextMessage` in de [publieke Parro-webapp](https://talk.parro.com/): afbeeldingsbijlagen gebruiken `attachmentType` en `entries`. Verwijderde berichten worden overgeslagen. Video’s en documenten worden in deze versie niet getoond.

## 0.2.0 — mededelingen en foto's op het dashboard

- Bundelt `custom:parro-card` met de bestaande HACS-integratie, inclusief visuele accountkeuze, titel, begrensd aantal mededelingen, optionele groepsfilter en fotoweergave.
- Voegt toegang per Home Assistant-gebruiker toe voor mededelingen en foto's. Beheerders hebben standaard toegang; andere gebruikers worden per Parro-account geselecteerd.
- Levert de kaartinhoud via aangemelde Home Assistant-routes en hergebruikt de feed vijf minuten. Bij een verbindingsfout kan een maximaal één uur oude lijst met een melding worden getoond. Foto's gebruiken een begrensde privé-cache; originele school- en bijlage-URL's worden niet aan de kaart doorgegeven.
- Registreert de kaartresource bij dashboards die hun resources via de interface beheren, met een handmatige route voor YAML-resources.
- Voegt een generiek voorbeelddashboard toe. De distributiehelper neemt uitsluitend het vastgelegde kaartbestand en de expliciete voorbeelden mee.

Lokaal gecontroleerd met 374 Python-tests en 14 browsercontroles. Mededelingen, foto's, groepsfilter, automatische kaartregistratie en visuele editor zijn na installatie live gecontroleerd. Toegang en intrekking voor andere gebruikers zijn synthetisch getest. De bestaande vier beheerdersacties blijven beschikbaar, waaronder de leesacties voor gesprekken.

## 0.1.2 — aanvullende correctie aanmelding

- Accepteert de callbackvorm `parro://oauth2:443/` die voorkomt in de [aanmeldtests van de vastgezette Parro-SDK](https://github.com/anneschuth/parro-cli/blob/4e0de03ff6c47ccaf1d99b1abd7e8b7643f95df0/tests/test_login.py#L118-L120). De eerdere controle wees deze vorm ook bij een correcte `state` af.
- Behoudt de exacte controle van de oorspronkelijke OAuth-`state` en de beperking tot de verwachte callbackbestemming.

Lokaal gecontroleerd met **200 geslaagde tests**, inclusief de volledige aanmeldketen zonder accountkeuze en accountkeuze via header of XML. Code- en formatteringscontroles slagen.

Na de update naar 0.1.2 heeft de gebruiker een geslaagde aanmelding en de samenvatting met tellers bevestigd. De eerdere live poging met 0.1.1 mislukte nog met `state_mismatch`; de werkelijke callback van die eerdere poging is niet vastgesteld.

## 0.1.1 — correctie aanmeldproces

- Behoudt de oorspronkelijke OAuth-`state` wanneer de aanmeldserver het autorisatiepad hervat zonder een nieuwe `state` mee te geven. Een later aangeboden afwijkende waarde wordt afgewezen.
- Onderscheidt technische fouten in de aanmeldflow van geweigerde aanmeldgegevens, zodat een technische fout niet als een onjuist wachtwoord wordt gemeld.
- Logt bij een technische aanmeldfout uitsluitend een vooraf toegestane foutcategorie, zonder tokens, aanmeldgegevens of serverinhoud.

Lokaal gecontroleerd met **170 geslaagde tests** tegen Home Assistant Core 2026.8.3 en een gemockte Parro-server; Ruff-codecontrole geslaagd.

Na installatie van 0.1.1 via HACS en een herstart mislukte de nieuwe live aanmeldpoging nog met `state_mismatch`. Deze correctie verhelpt een gevonden fout in de afhandeling van het aanmeldproces; zij is niet bevestigd als oorzaak van de eerdere mislukte praktijkproef.

## 0.1.0 — eerste testversie

- Aanmelding in Home Assistant, keuze uit meerdere identiteiten, koppeling aan de echte account-ID en heraanmelding.
- Tokenverversing met eenmalig herstel van een API-lezing na een 401; geen tokenbestand van de Parro-CLI.
- Compacte sensoren voor verbinding, laatste synchronisatie, kinderen, groepen, ongelezen mededelingen en ongelezen gesprekken.
- Instelbare polling van 15–240 minuten, standaard 30 minuten.
- Vier begrensde leesacties voor mededelingen, gesprekken, berichten en kalender-URL's.
- Beperkte diagnostiek en uitsluitend bijlagemetadata; geen verzenden, markeren, downloads of periodiek ophalen van chatinhoud.
- Handmatige installatie-ZIP met inventaris en aparte voorbereiding van een HACS-repository.

Lokaal getest met een gemockte Parro-server en Home Assistant Core 2026.8.3. Download en installatie via HACS zijn daarna bevestigd; de accountaanmelding is later met versie 0.1.2 geslaagd.
