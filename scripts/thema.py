#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/mental.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "mental-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Gemessen am 25.08.2026 mit machbarkeit.py: 10.865 Arbeiten in zwoelf Monaten
# (29,8 pro Tag), 2.086 mit Europabezug, 741 mit Deutschlandbezug. Ueberschneidung
# mit den Schwesterhubs 12,4 Prozent - KI 2,9, Gender 2,8, Pflege 2,6.
#
# DER ZUSCHNITT IST DIE GANZE ARBEIT. Die Krankheitsbegriffe als [Majr] allein
# ergeben 46.315 Arbeiten (126,9 pro Tag) und fast reine klinische Psychiatrie;
# nur die Dienste ergeben 7.040 (19,3 pro Tag). Tragfaehig ist allein die
# Verknuepfung Stoerung UND Versorgung, beides als HAUPTschlagwort: [Majr] statt
# [MeSH Terms] auf der Versorgungsseite ist der Hebel. Versorgungsbegriffe im
# Titel zusaetzlich brachten 75 Arbeiten und wurden wieder gestrichen.
# Wer hier etwas aendert, misst danach neu:
#     py machbarkeit.py kandidaten/psychische-gesundheit.json --titel
_THEMA = (
    '(((("Mental Health Services"[Majr] OR "Community Mental Health Services"[Majr] '
    'OR "Psychiatric Department, Hospital"[Majr] OR "Hospitals, Psychiatric"[Majr] '
    'OR "Mental Health"[Majr] OR "Psychiatry"[Majr] OR "Deinstitutionalization"[Majr] '
    'OR "Crisis Intervention"[Majr] OR "Psychotherapy"[Majr] '
    'OR "Community Psychiatry"[Majr] OR "Psychiatric Rehabilitation"[Majr] '
    'OR "Commitment of Mentally Ill"[Majr] OR "Emergency Services, Psychiatric"[Majr] '
    'OR "Mental Health Recovery"[Majr] OR "Suicide Prevention"[Majr]) '
    'OR (("Mental Disorders"[Majr] OR "Depressive Disorder"[Majr] OR "Depression"[Majr] '
    'OR "Anxiety Disorders"[Majr] OR "Schizophrenia"[Majr] OR "Bipolar Disorder"[Majr] '
    'OR "Stress Disorders, Post-Traumatic"[Majr] OR "Suicide"[Majr] '
    'OR "Psychotic Disorders"[Majr] OR "Feeding and Eating Disorders"[Majr] '
    'OR "Attention Deficit Disorder with Hyperactivity"[Majr] '
    'OR "Autism Spectrum Disorder"[Majr] '
    'OR "Personality Disorders"[Majr]) AND ("Health Services Accessibility"[Majr] '
    'OR "Delivery of Health Care"[Majr] OR "Health Services Needs and Demand"[Majr] '
    'OR "Patient Acceptance of Health Care"[Majr] OR "Primary Health Care"[Majr] '
    'OR "Referral and Consultation"[Majr] OR "Health Policy"[Majr] '
    'OR "Quality of Health Care"[Majr] OR "Waiting Lists"[Majr] '
    'OR "Patient Readmission"[Majr] OR "Community Health Services"[Majr] '
    'OR "Health Care Costs"[Majr] OR "Cost of Illness"[Majr] '
    'OR "Healthcare Disparities"[Majr] OR "Insurance, Health"[Majr] '
    'OR "Continuity of Patient Care"[Majr] OR "Patient Care Team"[Majr] '
    'OR "Health Services Research"[Majr]))) AND ("Mental Disorders"[MeSH Terms] '
    'OR "Mental Health"[MeSH Terms] OR "Psychiatry"[MeSH Terms])) '
    'NOT ("Psychometrics"[Majr] OR "Reproducibility of Results"[Majr] '
    'OR "Surveys and Questionnaires"[Majr]) NOT ("Artificial Intelligence"[Majr] '
    'OR "Machine Learning"[Majr] OR "Deep Learning"[Majr] OR "Telemedicine"[Majr] '
    'OR "Medical Informatics"[Majr] OR "Nursing"[Majr] OR "Nursing Care"[Majr] '
    'OR "Long-Term Care"[Majr] OR "Nursing Homes"[Majr] OR "Caregivers"[Majr] '
    'OR "Health Literacy"[Majr] OR "Patient Education as Topic"[Majr] '
    'OR "Climate Change"[Majr] OR "Air Pollution"[Majr] OR "Vaccination"[Majr] '
    'OR "Vaccines"[Majr] OR "Immunization"[Majr] OR "Aging"[Majr] OR "Longevity"[Majr] '
    'OR "Frailty"[Majr] OR "Geriatrics"[Majr] OR "Noncommunicable Diseases"[Majr] '
    'OR "Multimorbidity"[Majr] OR "Obesity"[Majr] OR "Bariatric Surgery"[Majr] '
    'OR "Patient Safety"[Majr] OR "Medical Errors"[Majr] OR "Cross Infection"[Majr] '
    'OR "Sepsis"[Majr]))'
)
_KONTEXT = (
    '("Delivery of Health Care"[MeSH Terms] OR "Health Services"[MeSH Terms] '
    'OR "Quality of Health Care"[MeSH Terms] OR "Patient Care"[MeSH Terms] '
    'OR "Health Policy"[MeSH Terms] OR "Public Health"[MeSH Terms] '
    'OR "health care"[Title/Abstract] OR "health services"[Title/Abstract] '
    'OR "patient outcome*"[Title/Abstract] OR "clinical practice"[Title/Abstract] '
    'OR implementation[Title/Abstract] OR patients[Title/Abstract])'
)
# "Humans"[MeSH] haelt Tier-, Labor- und reine Modellarbeiten heraus.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}) AND "Humans"[MeSH Terms])',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 30
POOL_ALLGEMEIN = 25
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 1
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
    "Du bist Fachredakteur fuer die Versorgung psychisch erkrankter "
    "Menschen. Aus einer Liste von PubMed-Abstracts waehlst du die "
    "relevantesten aktuellen Studien aus und fasst sie praezise auf Deutsch "
    "zusammen. Deine Leserschaft arbeitet im deutschen Gesundheitswesen: "
    "Kliniken, Praxen, Psychotherapie, gemeindepsychiatrische Traeger, "
    "Kostentraeger, Selbstverwaltung und Gesundheitspolitik. Sie will "
    "wissen, wer Hilfe wann erreicht und was daran zu aendern ist - nicht, "
    "welches Verfahren im Einzelfall um wie viele Skalenpunkte wirkt."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) die Versorgung psychisch erkrankter Menschen untersuchen - Zugang, Wartezeit, Behandlungsformen, Uebergaenge zwischen den Sektoren, Zwang und Rechte, Praevention oder die Krankheitslast, sofern daraus Handlungsbedarf erkennbar wird UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
      1. Zugang und Wartezeit: Wer erreicht Hilfe, wer nicht, und was hat daran
         messbar etwas geaendert - Terminvergabe, offene Sprechstunden, Stepped
         Care, Lotsen, aufsuchende Angebote.
      2. Versorgungsformen und ihre Ergebnisse: gemeindenahe Behandlung, Home
         Treatment, Tageskliniken, Krisendienste, Genesungsbegleitung - gemessen
         an Wiederaufnahmen, Verweildauer, Teilhabe oder patientenberichteten
         Ergebnissen.
      3. Uebergaenge und Schnittstellen: Entlassung, Nachsorge, die Grenze
         zwischen ambulant und stationaer, zwischen Erwachsenen- und
         Jugendpsychiatrie, zwischen Medizin und Eingliederungshilfe.
      4. Zwang, Rechte und Stigmatisierung: Unterbringung, Fixierung,
         Behandlung gegen den Willen - und was sie nachweislich verringert.
      5. Praevention und Frueherkennung, darunter Suizidpraevention.
      6. Ungleichheit: Wer wird schlechter versorgt - nach Einkommen, Bildung,
         Region, Sprache, Migrationsgeschichte - und was hilft dagegen.

NICHT in die Auswahl gehoeren:
Neurobiologie, Bildgebung, Genetik und Tiermodelle, Wirksamkeitsstudien einzelner
Wirkstoffe ohne Versorgungsbezug, Phase-I- und Phase-II-Studien, Validierungen von
Fragebogen, Skalen und Testverfahren, psychometrische Arbeiten, Fallberichte und
Fallserien, reine Praevalenzmeldungen ohne Bezugsgroesse sowie Uebersichten, die
nichts Eigenes berichten.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
      1. MINDESTENS DREI der sechs Studien muessen aus Europa stammen oder ein
         europaeisches Gesundheitssystem betreffen. Liegen weniger als drei solche
         Arbeiten vor, nimm die verbleibenden Plaetze aus dem Rest - aber schoepfe
         die europaeischen zuerst aus.
      2. HOECHSTENS ZWEI der sechs duerfen reine Wirksamkeitsstudien zu einem
         Therapieverfahren sein - Psychotherapie, Pharmakotherapie, ein einzelnes
         Programm. Dieser Teil des Feldes publiziert um ein Vielfaches mehr als
         der Rest; ohne die Grenze liest sich der Hub wie eine Zeitschrift fuer
         Therapieforschung statt wie ein Versorgungsportal.
      3. HOECHSTENS EINE darf eine digitale Anwendung, eine App oder ein
         Verfahren des maschinellen Lernens im Mittelpunkt haben. Digital Mental
         Health ist der am schnellsten wachsende Teil des Feldes, und der KI-Hub
         ist mit 2,9 Prozent der groesste Nachbar - ohne diese Grenze verschoebe
         sich der Hub binnen Wochen nach ki.m-vf.de.
      4. HOECHSTENS EINE darf ausschliesslich Praevalenz oder Krankheitslast
         beschreiben, ohne eine Massnahme, eine Ursache oder eine Folge zu
         untersuchen.
      5. HOECHSTENS EINE darf ausschliesslich Suchterkrankungen betreffen; sie
         sind ein eigenes Versorgungssystem mit eigener Finanzierung.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Nicht die Wirksamkeit entscheidet, was hier
ankommt, sondern der Zugang - und der haengt an deutschen Besonderheiten. Die
Richtlinienpsychotherapie ist eine Kassenleistung, aber an die Zulassung und die
Bedarfsplanung gebunden; die Terminservicestellen vermitteln Sprechstunden, nicht
Therapieplaetze. Neben den Kassen finanziert die Rentenversicherung Rehabilitation
und die Eingliederungshilfe die Teilhabe - eine Aufteilung, die es in dieser Form
kaum anderswo gibt. Psychiatrische Institutsambulanzen und die
stationsaequivalente Behandlung nach Paragraf 115d SGB V sind deutsche
Sonderformen; Krisendienste sind Laendersache und deshalb regional sehr
verschieden. Unterbringung und Zwangsbehandlung richten sich nach den
PsychKG-Gesetzen der Laender und dem Betreuungsrecht des BGB - Studien aus
Laendern mit Community Treatment Orders (England, Australien, Kanada) beschreiben
ein Instrument, das es hier nicht gibt. Ordne die Systeme nach Vergleichbarkeit:
hoch bei DACH und den Niederlanden, mittel bei Skandinavien, Frankreich, Belgien
und Grossbritannien, gering bei den USA. Nenne im Feld transfer ausdruecklich,
wer die Leistung dort bezahlt und wer den Zugang steuert.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel, **hoechstens 160 Zeichen**. Der
  Torwaechter lehnt alles ueber 200 Zeichen ab und stoppt damit die ganze
  Ausgabe - Methode und Population gehoeren nicht in den Titel, sie stehen
  in sum und transfer.
      **Er MUSS das Ergebnis nennen, nicht die Diagnose.** Abstracts sind nach
      der Stoerung betitelt; uebernimmt der Titel das, liest sich der Hub wie ein
      Diagnoseverzeichnis. Die Diagnose darf vorkommen, aber sie darf nicht allein
      stehen.
      Gut:      "Offene Sprechstunden halbierten die Wartezeit auf einen
                Therapieplatz"
      Schlecht: "Depression in der hausaerztlichen Versorgung: eine
                Querschnittstudie" (nennt nur die Diagnose)
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Beispiele fuer Begriffe, die englisch bleiben: Recovery, Home Treatment, Peer
Support, Stepped Care, Collaborative Care, Case Management, Assertive Community
Treatment, Patient-Reported Outcomes. Uebersetze dagegen, was im Deutschen eine
gaengige Entsprechung hat: aus "waiting time" wird die Wartezeit, aus
"treatment gap" die Behandlungsluecke, aus "coercion" die Zwangsbehandlung,
aus "involuntary admission" die Unterbringung, aus "physical restraint" die
Fixierung, aus "community mental health services" die gemeindenahe Versorgung,
aus "stigma" die Stigmatisierung.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""
