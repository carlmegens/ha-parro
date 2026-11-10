# Parro voor Home Assistant

Schoolmededelingen, gesprekken en beschikbare foto's openen vanuit je Parro-apparaat in Home Assistant. Eén HACS-installatie levert de integratie en de bijbehorende weergave, met toegang per account en gebruiker.

[![Open Parro in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=carlmegens&repository=ha-parro&category=integration)

**Versie 0.4.3 voegt een tab Agenda toe aan het Parro-scherm, naast Mededelingen en Gesprekken.** Schoolafspraken verschijnen automatisch in de gewone Home Assistant-agenda en zijn bruikbaar op eigen dashboards en in automatiseringen.

## Installeren via Marketplace of HACS

Vereist: Home Assistant Core **2026.8.3 of nieuwer**, Marketplace (vanaf Home Assistant 2026.11) of HACS en een Parro-/ParnasSys-account met de gewenste schoolinformatie. De knop hierboven opent deze repository in je eigen HACS-installatie.

1. Open **Parro** in HACS en download de integratie. Handmatig toevoegen kan via **Aangepaste repositories**, adres **https://github.com/carlmegens/ha-parro**, type **Integratie**.
2. Herstart Home Assistant.
3. Ga naar **Instellingen → Apparaten en diensten → Integratie toevoegen**, zoek **Parro** en meld je aan.
4. Kies de juiste identiteit wanneer het account meerdere ParnasSys-identiteiten aanbiedt.
5. Herlaad de browserpagina en open het Parro-apparaat bij deze integratie.

Installeer de nieuwste stabiele GitHub-release. Zolang de repository nog niet in de standaardcatalogus staat, voeg je hem als aangepaste repository toe. Zie de [Marketplace-catalogusuitleg](https://contributors.home-assistant.io/marketplace/guides/catalog/).

## Lezen vanuit het Parro-apparaat

1. Open **Instellingen → Apparaten en diensten → Parro** en open het gekoppelde Parro-apparaat of de gekoppelde dienst.
2. Klik op **Ongelezen mededelingen** voor de mededelingen met beschikbare foto's.
3. Klik op **Ongelezen gesprekken** om een gesprek te kiezen en recente berichten te lezen.

De twee bestaande tellers blijven gewone tellers. De pop-up haalt de inhoud afzonderlijk op voor het account van dat apparaat. De lijst is begrensd; de weergave toont geen volledig archief en is niet beperkt tot ongelezen inhoud.

De apparaatpagina biedt ook een knop om de gekoppelde Parro-weergave te openen. Die opent het meegeleverde Parro-scherm binnen Home Assistant, zonder een apart dashboard aan te maken. De normale **Configureren**-opties blijven beschikbaar. Een browserherlaadactie na installeren of bijwerken zorgt dat de nieuwe pop-upcode is geladen.

## Schoolagenda

Open de tab **Agenda** in het Parro-scherm voor een chronologische lijst van maximaal 20 komende of lopende afspraken binnen 365 dagen. De lijst gebruikt de schoolagenda van het gekozen account en toont datum, tijd, locatie en hele dagen. Vernieuw handmatig of open de volledige Home Assistant-agenda vanuit de lijst. Zonder gekoppelde schoolagenda verschijnt een duidelijke melding.

Op de apparaatpagina staat **Volgende schoolafspraak**, met de datum en tijd van de eerstvolgende afspraak die nog moet beginnen. Klik voor een chronologische lijst van maximaal 20 komende of nog lopende afspraken binnen 365 dagen, inclusief titel, datum, begin- en eindtijd, locatie en hele dagen. Vanuit de pop-up kun je de volledige Agenda openen. De lijst vernieuwt elke vijf minuten zolang de pop-up zichtbaar is, of met de vernieuwknop. Na een update kan eenmaal herladen van de browser nodig zijn. De datum wordt in de tijdzone van Home Assistant weergegeven. Als binnen de komende 365 dagen geen volgende afspraak bekend is, heeft deze datumsensor geen waarde; Home Assistant toont dan **Onbekend**. Bij een ophaalfout staat hij op **Niet beschikbaar**. Een begonnen afspraak schuift binnen een minuut door naar de volgende, zonder extra downloads.

De gewone kalenderentiteit blijft beschikbaar voor de zijbalk en automatiseringen. Daar betekent **Aan** dat er nu een afspraak bezig is en **Uit** dat er nu geen afspraak bezig is; dit is geen aan/uitschakelaar voor synchronisatie.

Na installeren of bijwerken en herstarten verschijnt **Parro Schoolagenda** op het Parro-apparaat en onder **Agenda** in de zijbalk. Selecteer deze agenda om de schoolafspraken te zien. Voor een eigen dashboard gebruik je de ingebouwde **Agenda**-kaart met de nieuwe `calendar`-entiteit; voor automatiseringen de gewone agendatriggers of `calendar.get_events`.

De integratie leest de iCal-abonnementen van het aangemelde account automatisch. Hele dagen, tijdzones, terugkerende afspraken, uitzonderingen en annuleringen worden verwerkt. De agenda is alleen-lezen en ververst ongeveer elke 30 minuten. Afspraken moeten door Parro in het agenda-abonnement worden aangeboden; berichten die een datum noemen worden niet automatisch afspraken. Een bestaand, los geïmporteerd Parro-abonnement blijft bestaan: selecteer één van beide agenda's om dubbele weergave te voorkomen.

**Zichtbaarheid:** de agenda volgt de normale Home Assistant-rechten voor entiteiten. De aparte Parro-instellingen voor mededelingen en gesprekken beperken deze agenda niet. Titel, tijd, omschrijving en locatie van de eerstvolgende afspraak staan in agenda-attributen; de sensor Volgende schoolafspraak bevat ook tijd, titel en locatie. Deze gegevens kunnen daardoor in de Home Assistant-geschiedenis terechtkomen. Abonnementslinks en ruwe iCal-inhoud blijven alleen in het geheugen en worden niet als attributen of diagnostiek gedeeld. Schakel zowel de agenda-entiteit als de sensor Volgende schoolafspraak uit als je deze informatie niet in Home Assistant wilt hebben.

Een agenda-aanvraag mag maximaal 366 dagen beslaan en 5.000 afspraken opleveren. Maximaal tien abonnementen worden samengevoegd; gelijke afspraken worden ontdubbeld. Onbereikbare of ongeldige agenda-inhoud geeft een fout of een niet-beschikbare agenda, zonder een gedeeltelijke of verouderde lijst als actueel te presenteren.

## Optioneel: een kaart op een eigen dashboard

1. Kies op je dashboard **Dashboard bewerken → Kaart toevoegen** en zoek **Parro**.
2. Kies in de visuele editor het gekoppelde Parro-account.
3. Stel de titel, het aantal mededelingen en de fotoweergave in en sla de kaart op.

De kaart toont standaard vijf mededelingen met beschikbare foto's. Je kunt 1–20 mededelingen kiezen en desgewenst op één groep filteren. Deze extra kaart is optioneel; de apparaatpop-ups werken zonder dashboardconfiguratie.

Voor handmatig toevoegen kun je beginnen met onderstaande configuratie en daarna het account in de visuele editor kiezen:

```yaml
type: custom:parro-card
```

Het account is vereist voordat een handmatig toegevoegde kaart inhoud kan ophalen. Voor gebruik op een eigen dashboard staat een generiek [voorbeeld met toelichting](examples/README.md) klaar. Het voorbeeld gebruikt uitsluitend invulvelden voor de eigen configuratie.

## Andere gebruikers toegang geven

Home Assistant-beheerders hebben standaard toegang. Om een andere gebruiker mee te laten lezen, open je **Instellingen → Apparaten en diensten → Parro → Configureren**. De rechten zijn afzonderlijk instelbaar:

- **Toegang tot mededelingen en foto’s** geeft toegang tot mededelingen en bijbehorende foto's.
- **Gezinsgebruikers met toegang tot gesprekken** geeft toegang tot gesprekken. Toegang tot mededelingen geeft dit recht niet automatisch.

Toegang geldt per gekoppeld Parro-account. De weergave biedt alleen accounts aan die de ingelogde Home Assistant-gebruiker voor die inhoud mag lezen. Het delen van een dashboard, zien van een teller of invullen van een account-ID verleent op zichzelf geen toegang. Een beheerder kan de geselecteerde gebruikers later weer verwijderen. De bestaande vier leesacties blijven voor beheerders en automatiseringen beschikbaar; deze instellingen geven daarop geen extra rechten.

## Meegeleverde weergave controleren

De integratie laadt de pop-upcode via Home Assistants globale modulevoorziening. Je hoeft hiervoor niet eerst een dashboard te openen. De apparaatlink opent een [meegeleverd paneel](https://www.home-assistant.io/integrations/panel_custom/) zonder extra zijbalkvermelding. De [interne apparaatlink](https://developers.home-assistant.io/docs/device_registry_index/) gebruikt de bestaande Home Assistant-verbinding.

Voor een optionele dashboardkaart geldt daarnaast het volgende:

Bij dashboardresources die Home Assistant via de interface beheert, registreert of actualiseert de integratie haar eigen kaartresource automatisch. Als **Parro** niet verschijnt of je **Custom element doesn't exist: parro-card** ziet, herlaad dan eerst de browserpagina.

Controleer zo nodig onder **Instellingen → Dashboards → menu → Resources / Bronnen** of deze resource eenmaal aanwezig is:

- URL: `/parro_static/parro-card.js?v=0.4.3`
- Type: **JavaScript-module**

Beheer je dashboardresources in YAML, voeg dan dit item toe aan de bestaande lijst met resources:

```yaml
- url: /parro_static/parro-card.js?v=0.4.3
  type: module
```

Zie de [officiële uitleg over resources](https://developers.home-assistant.io/docs/frontend/custom-ui/registering-resources/). De kaartcode staat in `custom_components/parro/frontend/parro-card.js` en wordt door de integratie aangeboden; je hoeft geen bestand naar `www` te kopiëren.

## Aanmelding, verversing en foto's

Voer het wachtwoord alleen in de Home Assistant-aanmeldflow in. Het blijft tijdelijk in het geheugen tijdens het aanmelden en wordt niet als instelling opgeslagen. Toegangs- en ververstokens worden in de Home Assistant-config entry bewaard; de Parro-CLI schrijft hiervoor geen tokenbestand. Behandel Home Assistant-back-ups als privégegevens.

De gekozen identiteit wordt aan de echte Parro-account-ID gekoppeld. Hetzelfde account kan niet dubbel worden toegevoegd. De integratie ververst tokens automatisch en herstelt een API-lezing na een 401 eenmaal met tokenverversing. Bij ingetrokken toegang vraagt Home Assistant om opnieuw aan te melden met hetzelfde account.

Via **Parro → Configureren** stel je het interval voor de statussensoren in: standaard **30 minuten**, toegestaan **15–240 minuten**. De kaart haalt haar mededelingen op aanvraag op en ververst elke **vijf minuten** zolang zij zichtbaar is. De server hergebruikt de opgehaalde lijst vijf minuten, zodat meerdere kaarten niet voortdurend dezelfde schoolinformatie opvragen. Bij een verbindingsfout kan de laatst opgehaalde lijst nog maximaal één uur worden getoond, met een melding dat de gegevens mogelijk verouderd zijn.

De gespreksweergave haalt maximaal 50 gesprekken op. Na het kiezen van een gesprek worden maximaal 20 berichten opgehaald; het gekozen gesprek moet bij de opgehaalde accountlijst horen. Ook deze inhoud wordt vijf minuten hergebruikt, met maximaal één uur oude inhoud als terugval bij een verbindingsfout. De samenvattingssensoren halen geen chatinhoud op. De selectie is begrensd en volledige bericht- of fotohistorie wordt niet gegarandeerd.

Foto's worden via een beveiligde Home Assistant-route aangeboden en tijdelijk in een begrensde privé-cache bewaard. De kaart krijgt geen originele school- of bijlage-URL's. Per mededeling worden maximaal drie foto's voorbereid; de kaart toont maximaal twaalf foto's tegelijk. Afbeeldingen worden als JPEG met maximaal 1600 pixels aan de langste zijde aangeboden. Dit is geen algemene bijlagedownloader.

Home Assistant heeft internettoegang nodig naar `inloggen.parnassys.net`, `rest-v2.parro.com` en de door Parro gebruikte, gecontroleerde afbeeldingsbestemmingen. De vastgezette afhankelijkheid is `parro==1.1.0`.

## Statussensoren

| Sensor | Betekenis |
| --- | --- |
| Verbinding | Verbindingsstatus van de statussynchronisatie. Een mislukte leesactie kan deze ook uitschakelen; een geslaagde statussynchronisatie herstelt de status. De kaart meldt haar eigen laadproblemen. |
| Laatste geslaagde synchronisatie | Tijdstip van de laatste geslaagde synchronisatie; blijft bij een storing op dat tijdstip staan. |
| Kinderen | Aantal gekoppelde kinderen, voor zover de API dit levert. |
| Groepen | Aantal gekoppelde groepen, voor zover de API dit levert. |
| Ongelezen mededelingen | Het door Parro geleverde aantal ongelezen mededelingen. Klik om mededelingen te openen. |
| Ongelezen gesprekken | Aantal chatrooms met ongelezen inhoud; geen aantal afzonderlijke chatberichten. Klik om gesprekken te openen. |

Ontbrekende aantallen zijn onbekend, nooit automatisch nul. Bij een volle begrensde lijst van 100 kinderen of groepen is het totaal onbekend. Bij een mislukte synchronisatie zijn tellers niet beschikbaar. De tellers en diagnostiek bevatten geen berichtteksten, kindnamen, foto's, bijlageadressen of iCal-URL's. Alleen de twee aanklikbare tellers bevatten niet-gevoelige verwijzingen naar de pop-up, het ingestelde account en de gekozen weergave.

## Leesacties voor automatiseringen

De vier bestaande acties leveren een antwoord terug via **Ontwikkelaarstools → Acties** of `response_variable` in een automatisering. Een handmatige actie vereist een Home Assistant-beheerder; automatiseringen zonder gebruikerscontext kunnen deze ook uitvoeren.

Alle acties vereisen `config_entry_id` van het gekozen Parro-account. De actie-interface biedt hiervoor een integratiekiezer. `limit` is optioneel: standaard **20**, minimaal **1**, maximaal **50**. Het antwoord bevat `items`, `returned` en `limit`; een selectie is geen volledig archief.

| Actie | Extra invoer | Antwoorditems |
| --- | --- | --- |
| `parro.get_announcements` | — | Mededelingen met geselecteerde velden en bijlagemetadata. |
| `parro.get_chatrooms` | — | Gesprekken met identificatie voor een vervolgopvraag. |
| `parro.get_messages` | `chatroom_id` | Berichten uit één gesprek. |
| `parro.get_calendar_urls` | — | Privé-iCal-abonnementslinks voor beheerders; de schoolagenda leest afspraken automatisch. |

`chatroom_id` is een positief numeriek ID van maximaal 20 cijfers, afkomstig uit `get_chatrooms`. Voorbeeld van een actiestap:

```yaml
action: parro.get_announcements
data:
  config_entry_id: VUL_PARRO_CONFIG_ENTRY_ID_IN
  limit: 10
response_variable: schoolmededelingen
```

Lees daarna `schoolmededelingen['items']` uit. Deze antwoorden kunnen privé-inhoud en kalenderadressen bevatten en zichtbaar worden in automatiseringstraces of in de bestemming die je zelf kiest. De acties leveren voor bijlagen uitsluitend metadata; foto-inhoud voor de kaart loopt via de afzonderlijke beveiligde route.

Voor eigen toepassingen zijn aangemelde HTTP-lezingen beschikbaar met dezelfde toegangscontrole:

| Route | Inhoud |
| --- | --- |
| `/api/parro/{config_entry_id}/feed?limit=5` | Mededelingen, 1–20; optioneel `group_id`. |
| `/api/parro/{config_entry_id}/conversations?limit=50` | Gesprekken, 1–50; vereist gespreksrecht. |
| `/api/parro/{config_entry_id}/messages?chatroom_id=123&limit=20` | Berichten uit het gekozen gesprek, 1–20; vereist gespreksrecht. |

Gebruik `GET` met de gebruikelijke Home Assistant-authenticatie; zet geen toegangstoken in de URL of in dashboard-YAML. De weergave gebruikt de overeenkomstige Home Assistant-WebSocketverbinding.

Periodieke statussynchronisatie leest geen chatinhoud. Deze versie biedt geen verzenden, markeren als gelezen, absenties, inschrijven, volledige archiefexport of AI-aansluiting. Eventuele effecten van leesaanroepen op de leesstatus aan de serverkant zijn nog niet volledig live beproefd.

## Problemen oplossen

- **De teller opent geen Parro-pop-up:** herlaad de browserpagina na de update. Gebruik als terugval de knop naar Parro op dezelfde apparaatpagina. In de veilige modus van Home Assistant worden extra frontendmodules niet geladen.
- **Geen kaart in de kaartkiezer:** herlaad de browser en controleer de kaartresource zoals hierboven beschreven.
- **Geen account om te kiezen of geen toegang:** controleer of Parro is aangemeld en of de ingelogde Home Assistant-gebruiker beheerder is of toegang heeft gekregen bij de Parro-opties.
- **Een foto ontbreekt:** niet elke bijlage is een ondersteunde foto. De kaart begrenst het aantal foto's; een geweigerde of niet beschikbare afbeelding maakt de mededeling niet onleesbaar.
- **Aanmeldgegevens geweigerd:** controleer het account via Parro zelf. Deze integratie gebruikt een gebruikersnaam/wachtwoordflow; andere aanmeldvarianten zijn niet live gevalideerd.
- **Technische aanmeldfout:** werk bij naar de nieuwste versie, herstart Home Assistant en begin een nieuwe aanmelding. De fout betekent niet automatisch dat het wachtwoord onjuist is. De integratie logt alleen een vaste technische foutcategorie.
- **Verbinding uit of tellers niet beschikbaar:** wacht op de volgende synchronisatie of herlaad de integratie eenmaal. Bij een authenticatieprobleem biedt Home Assistant heraanmelding aan.

Diagnostiek bevat beperkte technische status. Deel geen wachtwoorden, tokens, kalender-URL's, schoolberichten of foto's in een probleemmelding.

## Handmatige installatie en ontwikkeling

Download de repository via **Code → Download ZIP**. Kopieer de volledige map `custom_components/parro` naar de Home Assistant-configuratiemap, zodat `<config>/custom_components/parro/manifest.json` bestaat. Herstart Home Assistant, herlaad de browser en open na aanmelden het Parro-apparaat. Bij handmatig bijwerken vervang je de volledige integratiemap; bewaar een eventuele reservekopie buiten `custom_components`.

Voor de testomgeving is Python **3.14.2 of nieuwer binnen 3.14** nodig. Voer vanuit deze repository uit:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/prepare_repository.py --check
.venv/bin/python scripts/prepare_repository.py --local-archive dist/parro-0.4.0-local.zip
```

GitHub Actions voert HACS-validatie, Hassfest, Python-tests op Home Assistant 2026.8.3 en 2026.10.4 en browsertests uit. Alle controles moeten slagen voordat een release wordt gepubliceerd.

De meegeleverde kaart heeft ook [synthetische browsertests en een lokale voorvertoning](tests/frontend/README.md). Deze gebruiken de echte kaartcode met verzonnen accounts, berichten en lokaal getekende foto's. De installatiekaart zelf heeft geen Node-afhankelijkheden.

De installatie-ZIP bevat de integratie inclusief kaart, openbare documentatie en het generieke voorbeelddashboard. Een aparte SHA-256-inventaris vermeldt de inhoud. De helper weigert bestaande uitvoer te overschrijven en kopieert alleen expliciet toegestane bestanden. Overdrachtsnotities, lokale verslagen, tests, ontwikkelhulpbestanden, afhankelijkheidsmappen, screenshots en familie- of dashboardgegevens worden niet meegenomen. Synthetische tests blijven wel in de bronrepository beschikbaar voor onderhoud.

Voor een nieuwe lokale publicatiemap kun je `scripts/prepare_repository.py` gebruiken met `--output`, `--owner`, `--repo` en `--codeowner`. De helper controleert de lokale structuur en publicatiemetadata, waaronder niet ingevulde waarden. Hij installeert of publiceert niets en neemt geen contact op met GitHub of Parro.

## Licentie

De eigen integratie en kaart vallen onder de [MIT-licentie](LICENSE). De apart geïnstalleerde afhankelijkheid [`parro` 1.1.0](https://github.com/anneschuth/parro-cli/releases/tag/v1.1.0) behoudt haar eigen licentie en auteursrecht. Dit project is onofficieel en wordt niet door Parro, ParnasSys of Home Assistant ondersteund.
