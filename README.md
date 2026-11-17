# Parro voor Home Assistant

Schoolmededelingen, gesprekken, beschikbare foto's en schoolafspraken openen vanuit je Parro-apparaat in Home Assistant. Eén installatie via Marketplace of HACS levert de integratie en de bijbehorende weergave, met toegang per account en gebruiker.

[![Open Parro in Marketplace of HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=carlmegens&repository=ha-parro&category=integration)

**Beschikbaar in de standaardcatalogus van Marketplace en HACS.** Zoek op **Parro** of gebruik de installatieknop hierboven; een aangepaste repository toevoegen is niet nodig. De [catalogusaanvraag is op 16 november 2026 goedgekeurd en samengevoegd](https://github.com/hacs/default/pull/13845). Dit is een onofficiële community-integratie voor Parro.

**Versie 1.0.0 is de eerste stabiele release.** Mededelingen, gesprekken, foto’s en de schoolagenda zijn beschikbaar vanuit het Parro-apparaat en het meegeleverde Parro-scherm. Schoolafspraken werken ook in de gewone Home Assistant-agenda, op eigen dashboards en in automatiseringen.

## Installeren via Marketplace of HACS

Vereist: Home Assistant Core **2026.8.3 of nieuwer**, Marketplace (vanaf Home Assistant 2026.11) of HACS en een Parro-/ParnasSys-account met de gewenste schoolinformatie. De knop hierboven opent Parro in de Marketplace of HACS van je eigen Home Assistant.

1. Open **Marketplace** of **HACS**, zoek op **Parro** en installeer de integratie van **carlmegens/ha-parro**. Kies de nieuwste stabiele release.
2. Herstart Home Assistant.
3. Ga naar **Instellingen → Apparaten en diensten → Integratie toevoegen**, zoek **Parro** en meld je aan.
4. Kies de juiste identiteit wanneer het account meerdere ParnasSys-identiteiten aanbiedt.
5. Herlaad de browserpagina en open het Parro-apparaat bij deze integratie.

**Parro nog niet zichtbaar?** Vernieuw de catalogus of gebruik de installatieknop hierboven om de repository rechtstreeks te openen.

Heb je Parro al via een aangepaste repository geïnstalleerd? Je hoeft niets opnieuw te installeren: de bestaande installatie blijft updates ontvangen via Marketplace of HACS.

## Versies en compatibiliteit

Versie **1.0.0** bouwt voort op de functionaliteit van 0.4.3. Bijwerken vereist geen nieuwe aanmelding, gewijzigde kaartconfiguratie of migratie van entiteiten. Installeer de update via Marketplace of HACS en herstart Home Assistant.

Binnen **1.x** behouden we de bestaande entiteit-identiteiten en de gedocumenteerde acties, API-antwoorden en kaartinstellingen. Foutcorrecties krijgen een patchversie (bijvoorbeeld 1.0.1); compatibele uitbreidingen een minorversie (bijvoorbeeld 1.1.0). Incompatibele wijzigingen aan deze interfaces krijgen een nieuwe hoofdversie en migratie-instructies. De minimale Home Assistant-versie staat per release in `hacs.json`; wijzigingen daarin vermelden we in de releasenotities.

De beschreven grenzen voor geschiedenis, bijlagen, agenda-inhoud en aanmelding blijven gelden. De integratie is afhankelijk van de Parro-dienst. Zij leest standaard alleen; de optionele antwoordfunctie vereist afzonderlijk inschakelen en een lijst met toegestane gesprekken.

## Lezen vanuit het Parro-apparaat

1. Open **Instellingen → Apparaten en diensten → Parro** en open het gekoppelde Parro-apparaat of de gekoppelde dienst.
2. Klik op **Ongelezen mededelingen** voor de mededelingen met beschikbare foto's.
3. Klik op **Ongelezen gesprekken** om een gesprek te kiezen en recente berichten te lezen.

De twee bestaande tellers blijven gewone tellers. De pop-up haalt de inhoud afzonderlijk op voor het account van dat apparaat. De lijst is begrensd; de weergave toont geen volledig archief en is niet beperkt tot ongelezen inhoud.

De apparaatpagina biedt ook een knop om de gekoppelde Parro-weergave te openen. Die opent het meegeleverde Parro-scherm binnen Home Assistant, zonder een apart dashboard aan te maken. De normale **Configureren**-opties blijven beschikbaar. Een browserherlaadactie na installeren of bijwerken zorgt dat de nieuwe pop-upcode is geladen.

## Testversie 1.1.0b1: optionele functies per gezin

**Deze functies zitten in de testrelease 1.1.0b1, nog niet in de stabiele 1.0.0.** Open Parro in Marketplace/HACS, kies via het repositorymenu opnieuw downloaden en toon test-/bètaversies als die optie beschikbaar is. Selecteer expliciet `v1.1.0b1` en herstart Home Assistant. Gebruik anders de installatie-ZIP van de [testrelease](https://github.com/carlmegens/ha-parro/releases/tag/v1.1.0b1). Voor teruggaan kies je opnieuw 1.0.0. De nieuwe entiteiten worden dan niet meer aangeboden; eigen kaarten die ernaar verwijzen moet je zelf aanpassen.

De uitbreiding is met verzonnen gegevens getest. De kindkoppelingen, profielfoto’s en daadwerkelijke aflevering van antwoorden zijn nog niet met een echt schoolaccount bevestigd. Er zijn tijdens de ontwikkeling geen berichten naar leerkrachten verzonden. Test antwoorden alleen met een bewust gekozen bericht; gebruik de officiële Parro-app om aflevering te controleren.

Ga naar **Instellingen → Apparaten en diensten → Parro → Configureren**. De nieuwe opties staan standaard uit, ook na bijwerken. Je bestaande tellers, agenda, kaarten en toegangsinstellingen blijven werken.

| Optie | Wat beschikbaar komt |
| --- | --- |
| Entiteiten per kind | Een eigen apparaat met voornaam, groepssensor en schoolagenda. |
| Foto-entiteiten | Zes vaste `image`-entiteiten met recente mededelingsfoto’s. Met kind-entiteiten ook een profielfoto per kind. |
| Gebeurtenissen | Twee `event`-entiteiten en gebeurtenissen `parro_new_announcement` en `parro_new_message` voor automatiseringen. |
| Antwoorden toestaan | De actie `parro.send_reply`, alleen voor expliciet toegestane directe- en familiegesprekken. |

**Per kind:** de agenda gebruikt Parro’s expliciete kindkoppelingen in de agenda-API. Afspraken zonder kindkoppeling blijven alleen in de bestaande accountagenda zichtbaar; er wordt niet op namen of groepstitels gegokt. De accountagenda blijft de bestaande iCal-bron gebruiken. Nieuwe kinderen worden bij een volgende verversing ontdekt; verdwenen kinderen worden niet beschikbaar. Oude apparaten worden niet automatisch verwijderd, zodat eigen dashboardconfiguratie niet verloren gaat. Groepsnamen kunnen meerdere groepen bevatten. Een ontbrekende profielfoto blijft niet beschikbaar.

**Foto’s op een dashboard:** voeg een ingebouwde **Afbeelding-entiteit / Picture entity**-kaart toe en kies een Parro-afbeelding. Er zijn maximaal zes recente foto’s uit de laatste vijftig mededelingen; de vaste posities wisselen met nieuwe inhoud en vormen geen archief. Foto’s uit privégesprekken blijven uitsluitend in de afgeschermde gesprekskaart. Foto’s worden op aanvraag geladen, verkleind tot maximaal 1600 pixels en opnieuw opgeslagen als JPEG zonder oorspronkelijke metadata. Externe foto-URL’s staan niet in entiteitsattributen.

**Zichtbaarheid:** de nieuwe kind-, agenda-, groeps- en foto-entiteiten vallen onder normale Home Assistant-toegang, niet onder de aparte gebruikerslijsten voor de Parro-kaart. Voornaam en entiteitsnamen blijven in de lokale registers staan. Groepsnamen zijn sensorwaarden en kunnen in de geschiedenis worden opgeslagen. Home Assistant gebruikt tokenlinks voor afbeelding-entiteiten; iemand met zo’n link kan de afbeelding mogelijk bekijken. Deel die links niet. Schakel de foto-optie uit om verdere levering te blokkeren. Reeds bekeken of gedownloade foto’s kunnen niet worden teruggehaald.

### Meldingen automatiseren

Nieuwe activiteit wordt bij het ingestelde verversingsinterval ontdekt, niet rechtstreeks gepusht. Na inschakelen, herladen of herstarten ontstaat eerst een stille beginstand: bestaande berichten geven geen melding. Dit is geen volledige berichtenstroom: de laatste vijftig mededelingen en vijftig gesprekken worden bekeken; per gesprek is alleen het laatste bericht bekend. Meerdere berichten tussen twee controles kunnen daardoor één gebeurtenis opleveren. Eigen antwoorden worden overgeslagen wanneer de afzender als eigen identiteit bekend is.

Elke gebeurtenis bevat uitsluitend `config_entry_id`, `item_id` en `published_at`. Bij chatberichten is `item_id` het gespreks-ID. Er worden geen namen, berichtteksten of fotolinks meegestuurd. Gebruik je eigen account-ID in dit voorbeeld:

```yaml
alias: Parro nieuwe mededeling
triggers:
  - trigger: event
    event_type: parro_new_announcement
    event_data:
      config_entry_id: VUL_JE_ACCOUNT_ID_IN
actions:
  - action: persistent_notification.create
    data:
      title: Parro
      message: Er is een nieuwe schoolmededeling beschikbaar.
```

Voor chatberichten gebruik je `parro_new_message`. De `event`-entiteiten kun je ook als statustrigger gebruiken, met een controle dat de vorige waarde niet `unknown` of `unavailable` was. Gebeurtenissen zijn voor automatiseringen beschikbaar en vallen niet onder de Parro-kaartrechten.

### Optioneel antwoorden

1. Haal het gespreks-ID op met `parro.get_chatrooms`.
2. Zet **Antwoorden toestaan** aan en voeg het ID toe aan **Gespreks-ID’s waarvoor antwoorden zijn toegestaan**.
3. Gebruik **Ontwikkelaarshulpmiddelen → Acties → Parro: Antwoord versturen**, of een zelf ingerichte automatisering.

De actie `parro.send_reply` heeft de velden `config_entry_id`, `chatroom_id` en `message`. Alleen beheerders en vertrouwde automatiseringen mogen deze actie aanroepen; leesrechten op de Parro-kaart geven geen schrijfrechten. Groepsgesprekken, gearchiveerde gesprekken en gesprekken waarin antwoorden door Parro is uitgeschakeld worden geweigerd. Er is nog geen antwoordveld in de Parro-kaart.

Een antwoord bevat maximaal 1000 tekens en 20 regels. Er geldt minimaal één minuut tussen pogingen in hetzelfde gesprek, maximaal vijf pogingen per uur en twintig per dag per account. Hetzelfde antwoord wordt zes uur tegengehouden. De lokale pogingadministratie bevat tijdstippen, gespreks-ID’s en hashes, geen tekst; deze blijft na herstart gelden en wordt bij het verwijderen van de integratie gewist. Oude pogingen worden bij de volgende poging opgeruimd. De tekst kan wel in Home Assistant-automatiseringstraces of eigen logging terechtkomen.

Er wordt nooit automatisch opnieuw verzonden na een onzekere uitkomst. **Controleer bij een fout eerst Parro zelf**: een timeout kan optreden nadat het bericht al ontvangen is. Het aanzetten van de optie verstuurt op zichzelf niets. Verstuur geen automatische antwoorden voordat je de betreffende automatisering zelf hebt gecontroleerd.

## Schoolagenda

Open de tab **Agenda** in het Parro-scherm voor een chronologische lijst van maximaal 20 komende of lopende afspraken binnen 365 dagen. De lijst gebruikt de schoolagenda van het gekozen account en toont datum, tijd, locatie en hele dagen. Vernieuw handmatig of open de volledige Home Assistant-agenda vanuit de lijst. Zonder gekoppelde schoolagenda verschijnt een duidelijke melding.

Op de apparaatpagina staat **Volgende schoolafspraak**, met de datum en tijd van de eerstvolgende afspraak die nog moet beginnen. Klik voor een chronologische lijst van maximaal 20 komende of nog lopende afspraken binnen 365 dagen, inclusief titel, datum, begin- en eindtijd, locatie en hele dagen. Vanuit de pop-up kun je de volledige Agenda openen. De lijst vernieuwt elke vijf minuten zolang de pop-up zichtbaar is, of met de vernieuwknop. Na een update kan eenmaal herladen van de browser nodig zijn. De datum wordt in de tijdzone van Home Assistant weergegeven. Als binnen de komende 365 dagen geen volgende afspraak bekend is, heeft deze datumsensor geen waarde; Home Assistant toont dan **Onbekend**. Bij een ophaalfout staat hij op **Niet beschikbaar**. Een begonnen afspraak schuift binnen een minuut door naar de volgende, zonder extra downloads.

De gewone kalenderentiteit blijft beschikbaar voor de zijbalk en automatiseringen. Daar betekent **Aan** dat er nu een afspraak bezig is en **Uit** dat er nu geen afspraak bezig is; dit is geen aan/uitschakelaar voor synchronisatie.

Na installeren of bijwerken en herstarten verschijnt **Parro Schoolagenda** op het Parro-apparaat en onder **Agenda** in de zijbalk. Selecteer deze agenda om de schoolafspraken te zien. Voor een eigen dashboard gebruik je de ingebouwde **Agenda**-kaart met de nieuwe `calendar`-entiteit; voor automatiseringen de gewone agendatriggers of `calendar.get_events`.

De integratie leest de iCal-abonnementen van het aangemelde account automatisch. Hele dagen, tijdzones, terugkerende afspraken, uitzonderingen en annuleringen worden verwerkt. De agenda is alleen-lezen en ververst ongeveer elke 30 minuten. Afspraken moeten door Parro in het agenda-abonnement worden aangeboden; berichten die een datum noemen worden niet automatisch afspraken. Een bestaand, los geïmporteerd Parro-abonnement blijft bestaan: selecteer één van beide agenda's om dubbele weergave te voorkomen.

**Zichtbaarheid:** de agenda volgt de normale Home Assistant-rechten voor entiteiten. De aparte Parro-instellingen voor mededelingen en gesprekken beperken deze agenda niet. Titel, tijd, omschrijving en locatie van de eerstvolgende afspraak staan in agenda-attributen; de sensor Volgende schoolafspraak bevat ook tijd, titel en locatie. In deze versie worden de inhoudelijke agenda-attributen en de titel/locatie van de volgende afspraak uitgesloten van nieuwe Recorder-opslag. Dat verwijdert geen bestaande geschiedenis en voorkomt geen opslag via eigen automatiseringen, meldingen of traces. Abonnementslinks en ruwe iCal-inhoud blijven alleen in het geheugen en worden niet als attributen of diagnostiek gedeeld. Schakel zowel de agenda-entiteit als de sensor Volgende schoolafspraak uit als je deze informatie niet in Home Assistant wilt hebben.

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

Zonder de nieuwe opties leest periodieke statussynchronisatie geen chatinhoud. Met gebeurtenissen of foto-entiteiten leest de integratie begrensde lijsten; zij opent daarvoor geen afzonderlijke gesprekken of berichten. Antwoorden is alleen beschikbaar met de expliciete optie en gesprekslijst. Er is geen actie voor markeren als gelezen, absenties, inschrijven, volledige archiefexport of AI-aansluiting. Eventuele effecten van leesaanroepen op de leesstatus aan de serverkant zijn nog niet volledig live beproefd.

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
.venv/bin/python scripts/prepare_repository.py --local-archive dist/parro-1.0.0-local.zip
```

GitHub Actions voert HACS-validatie, Hassfest, Python-tests op Home Assistant 2026.8.3 en 2026.10.4 en browsertests uit. Alle controles moeten slagen voordat een release wordt gepubliceerd.

De meegeleverde kaart heeft ook [synthetische browsertests en een lokale voorvertoning](tests/frontend/README.md). Deze gebruiken de echte kaartcode met verzonnen accounts, berichten en lokaal getekende foto's. De installatiekaart zelf heeft geen Node-afhankelijkheden.

De installatie-ZIP bevat de integratie inclusief kaart, openbare documentatie en het generieke voorbeelddashboard. Een aparte SHA-256-inventaris vermeldt de inhoud. De helper weigert bestaande uitvoer te overschrijven en kopieert alleen expliciet toegestane bestanden. Overdrachtsnotities, lokale verslagen, tests, ontwikkelhulpbestanden, afhankelijkheidsmappen, screenshots en familie- of dashboardgegevens worden niet meegenomen. Synthetische tests blijven wel in de bronrepository beschikbaar voor onderhoud.

Voor een nieuwe lokale publicatiemap kun je `scripts/prepare_repository.py` gebruiken met `--output`, `--owner`, `--repo` en `--codeowner`. De helper controleert de lokale structuur en publicatiemetadata, waaronder niet ingevulde waarden. Hij installeert of publiceert niets en neemt geen contact op met GitHub of Parro.

## Onafhankelijk project en beperkingen

Dit is een onafhankelijk communityproject, niet gemaakt, goedgekeurd of ondersteund door Parro, ParnasSys of Topicus. Ook opname in de Marketplace/HACS betekent geen goedkeuring door deze partijen. Merknamen en het Parro-logo blijven eigendom van hun respectieve rechthebbenden; gebruik in dit project dient ter herkenning van de gekoppelde dienst.

De integratie gebruikt onofficiële koppelingen. Wijzigingen bij Parro kunnen functies onderbreken of opnieuw aanmelden noodzakelijk maken. Er is geen garantie op volledigheid, beschikbaarheid of aflevering van meldingen en antwoorden. Houd de officiële Parro-app beschikbaar voor belangrijke schoolcommunicatie. De integratie geeft geen extra rechten op schoolinformatie of foto’s en omzeilt geen accountbeperkingen.

Publiceer geen schoolberichten, kindgegevens, foto’s, tokens of volledige logs in issues. Verwijder zulke gegevens ook uit screenshots. De integratie verstuurt geen telemetrie naar de ontwikkelaars. Home Assistant-back-ups kunnen lokale accounttokens, namen en eigen automatiseringsgegevens bevatten: behandel die als privé.

## Licentie en dank

De eigen integratie en kaart vallen onder de [MIT-licentie](LICENSE), zonder garantie zoals in die licentie beschreven. De gegevensmodellen voor kinderen, groepen en agenda-items zijn aangepast uit [Parro-HA van Paulus1337](https://github.com/Paulus1337/Parro-HA). Zijn auteursrecht en MIT-licentie zijn opgenomen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). De licentie op de code verleent geen rechten op Parro-merken, berichten of foto’s. De apart geïnstalleerde afhankelijkheid [`parro` 1.1.0](https://github.com/anneschuth/parro-cli/releases/tag/v1.1.0) behoudt haar eigen licentie en auteursrecht. Dit project is onofficieel en wordt niet door Parro, ParnasSys of Home Assistant ondersteund.
