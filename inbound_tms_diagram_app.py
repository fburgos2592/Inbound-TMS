"""inbound_tms_diagram_app.py

Interactive diagram viewer/editor for the Inbound TMS/CMS work:
- C4-style layering (Context, Containers, Domain)
- UML domain diagram
- Sequence diagrams (current-state + TMS overlay)

How it works
------------
This app renders PlantUML text by generating a URL to a PlantUML server.
It uses the official PlantUML deflate + custom base64 encoding so no Java
or local PlantUML install is required.

Run
---
1) Install Streamlit:
   pip install streamlit

2) Start the app:
   streamlit run inbound_tms_diagram_app.py

Notes
-----
- Rendering requires access to the selected PlantUML server.
- For best quality in docs/PowerPoint, use SVG.

"""

from __future__ import annotations

import textwrap
import zlib
from dataclasses import dataclass

import streamlit as st


# -------------------------
# PlantUML URL encoding
# -------------------------

_PLANTUML_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"


def _encode_6bit(b: int) -> str:
    if 0 <= b < 64:
        return _PLANTUML_ALPHABET[b]
    raise ValueError("6-bit value out of range")


def plantuml_encode(plantuml_text: str) -> str:
    """Encode PlantUML text into the compact URL-safe format used by PlantUML servers."""
    data = plantuml_text.encode("utf-8")
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed = compressor.compress(data) + compressor.flush()

    res = []
    i = 0
    while i < len(compressed):
        b1 = compressed[i]
        b2 = compressed[i + 1] if i + 1 < len(compressed) else 0
        b3 = compressed[i + 2] if i + 2 < len(compressed) else 0
        i += 3

        c1 = b1 >> 2
        c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
        c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F

        res.append(_encode_6bit(c1 & 0x3F))
        res.append(_encode_6bit(c2 & 0x3F))
        res.append(_encode_6bit(c3 & 0x3F))
        res.append(_encode_6bit(c4 & 0x3F))

    return "".join(res)


def plantuml_url(server_base: str, fmt: str, diagram_text: str) -> str:
    """Build a render URL for a PlantUML server.

    server_base examples:
      - https://www.plantuml.com/plantuml
      - https://render.powerplantuml.com/plantuml

    fmt: 'svg' or 'png'
    """
    encoded = plantuml_encode(diagram_text)
    server_base = server_base.rstrip("/")
    fmt = fmt.strip().lower()
    if fmt not in {"svg", "png"}:
        raise ValueError("fmt must be 'svg' or 'png'")
    return f"{server_base}/{fmt}/{encoded}"


# -------------------------
# Diagram content
# -------------------------

# C4-style diagrams WITHOUT external !include directives (most reliable across servers).

C4_LEVEL1_CONTEXT = r"""@startuml
skinparam Shadowing false
skinparam RoundCorner 10
skinparam backgroundColor white
skinparam ArrowColor #333333
skinparam actorStyle awesome

actor "Supply Planner" as SP
actor "Carrier / LSP" as CA

rectangle "Inbound TMS" as TMS #F7F7F7 {
  rectangle "Inbound TMS\n(Plans, executes, tracks inbound freight)" as TMSCore #FFFFFF
}

rectangle "ERP (Dynamics)" as ERP #FFFFFF
rectangle "WMS (Receiving)" as WMS #FFFFFF
rectangle "Cleo / EDI" as CLEO #FFFFFF

SP --> TMSCore : plans & monitors loads
CA --> TMSCore : tenders, tracking, BOL
TMSCore --> ERP : PO refs, costs, dates
TMSCore --> WMS : appts, receipts
TMSCore --> CLEO : partner messaging

@enduml"""

C4_LEVEL2_CONTAINERS = r"""@startuml
skinparam Shadowing false
skinparam RoundCorner 10
skinparam backgroundColor white
skinparam ArrowColor #333333
skinparam rectangle {
  BorderColor #333333
}

rectangle "Inbound TMS" as SYS #F7F7F7 {
  rectangle "Ops UI\n(Web)" as UI #FFFFFF
  rectangle "Inbound API\n(REST)" as API #FFFFFF
  rectangle "Domain Services\n(Load lifecycle + rules)" as DOM #FFFFFF
  database  "TMS DB\n(Loads, events, exceptions)" as DB
}

rectangle "Cleo / EDI" as CLEO #FFFFFF
rectangle "ERP" as ERP #FFFFFF
rectangle "WMS" as WMS #FFFFFF

UI --> API : HTTPS
API --> DOM : commands/queries
DOM --> DB : read/write
API --> CLEO : publish events / receive updates
CLEO --> ERP : EDI / APIs
CLEO --> WMS : files / APIs

@enduml"""

C4_LEVEL3_DOMAIN_REFINED = r"""@startuml
skinparam Shadowing false
skinparam RoundCorner 10
skinparam ClassAttributeIconSize 0
skinparam backgroundColor white
skinparam ArrowColor #333333

package "Core Aggregates" {
  class Load
  class Stop
  class PurchaseOrder
}

package "Execution & Control" {
  class LoadEvent
  class Exception
  class Cost
}

package "Scheduling" {
  class Appointment
}

Load "1" o-- "1..*" Stop
Load "1" o-- "0..*" PurchaseOrder
Load "1" o-- "0..*" LoadEvent
Load "1" o-- "0..*" Exception
Load "1" o-- "0..*" Cost
Stop "0..1" --> "1" Appointment

@enduml"""

# Full UML (your current page version, with immutability markers)
UML_FULL = r"""@startuml

' ===== Core Aggregates =====
class Load {
  load_id <<immutable>>
  status
  mode <<immutable_after_TENDERED>>
  equipment_type <<immutable_after_TENDERED>>
  planned_pickup_datetime <<immutable_after_IN_TRANSIT>>
  planned_delivery_datetime <<immutable_after_IN_TRANSIT>>
  actual_pickup_datetime <<immutable>>
  actual_delivery_datetime <<immutable>>
  total_weight <<immutable_after_TENDERED>>
  total_volume <<immutable_after_TENDERED>>
}

class Stop {
  stop_id <<immutable>>
  stop_type <<immutable_after_ARRIVAL>>
  sequence <<immutable_after_ARRIVAL>>
  planned_arrival
  planned_departure
  actual_arrival <<immutable>>
  actual_departure <<immutable>>
  service_time_minutes
}

class PurchaseOrder {
  po_number <<immutable>>
  status
  expected_quantity <<immutable>>
  received_quantity
}

' ===== Master Data =====
class Vendor {
  vendor_id <<immutable>>
  name
}

class Carrier {
  carrier_id <<immutable>>
  name
  mode_supported
}

class Facility {
  facility_id <<immutable>>
  name
  timezone
}

class Location {
  location_id <<immutable>>
  address
}

' ===== Scheduling =====
class Appointment {
  appointment_id <<immutable>>
  appointment_start <<immutable_after_CHECK_IN>>
  appointment_end <<immutable_after_CHECK_IN>>
  status
}

class Dock {
  dock_id <<immutable>>
  dock_type
  capacity_per_hour
}

' ===== Execution & Control =====
class LoadEvent {
  event_id <<immutable>>
  event_type <<immutable>>
  event_timestamp <<immutable>>
  source <<immutable>>
}

class Exception {
  exception_id <<immutable>>
  exception_type <<immutable>>
  severity
  detected_at <<immutable>>
  resolved_at
}

class Cost {
  cost_id <<immutable>>
  cost_type <<immutable>>
  expected_amount <<immutable_after_TENDERED>>
  actual_amount <<immutable_after_INVOICED>>
  variance
}

class ExternalReference {
  external_system <<immutable>>
  external_id <<immutable>>
  entity_type <<immutable>>
}

' ===== Relationships =====
Load "1" o-- "1..*" Stop
Load "1" o-- "0..*" PurchaseOrder
Load "1" o-- "0..*" LoadEvent
Load "1" o-- "0..*" Exception
Load "1" o-- "0..*" Cost
Load "1" --> "1" Carrier
Load "1" --> "1" Facility

Stop "*" --> "1" Location
Stop "0..1" --> "1" Appointment

Appointment "*" --> "1" Dock
Dock "*" --> "1" Facility

PurchaseOrder "*" --> "1" Vendor

Cost "*" --> "1" Carrier

ExternalReference "*" --> "1" Load
ExternalReference "*" --> "1" PurchaseOrder

@enduml"""

SEQUENCE_CURRENT = r"""@startuml

autonumber
hide footbox

actor "Supply Planner" as SP
participant "Inbound Logistics" as IL
participant "Shipper" as SH
participant "Carrier / LSP" as CA
participant "WMS (Appointment Scheduling)" as WMS
participant "PO System (ERP)" as ERP
participant "Voyage Header / Reporting" as VH

== Load Building & Planning ==
SP -> IL: Add order details to "Load Request File"
IL -> IL: Review for errors / inconsistencies / required info
alt Information incomplete or inaccurate
  IL -> SP: Request clarification
  SP -> IL: Provide clarification / corrections
end
IL -> IL: Aggregate orders & calculate weights (partials)
IL -> IL: Identify temp-compatible orders
alt Load plan does not work
  IL -> SP: Ask planners to add/cut to make load work
  SP -> IL: Adjust orders to fill truck & maximize freight
end

== Freight Booking ==
IL -> IL: Check contract parameters / obligations
alt Load meets contract parameters
  IL -> CA: Notify LSP via email (contract loads)
  CA -> IL: Confirm coverage
  IL -> CA: Send load tender (Excel)
  CA -> IL: Confirm receipt
else Load does NOT meet contract parameters
  IL -> CA: Email "Bid Template" to all LSPs (BCC)
  CA -> IL: Submit rates
  IL -> IL: Aggregate bids & award (price + service)
  IL -> CA: Award notice / tender
  CA -> IL: Confirm
end

== Load Execution ==
CA -> CA: Add load to daily tracking file
CA -> SH: Call shipper to validate tender info (PU#, shed, etc.)
alt Discrepancy found during validation
  CA -> IL: Email discrepancy (PU#, shed location, etc.)
  IL -> IL: Troubleshoot independently
  alt Inbound cannot resolve
    IL -> SP: Request clarification
    SP -> IL: Provide clarification
  end
  IL -> CA: Provide corrected information
end

CA -> SH: Day-of pickup: count confirmation & PU appts (if applicable)
CA -> IL: Send count confirmation details
alt Discrepancy found during count confirmation
  CA -> IL: Report discrepancy
  IL -> IL: Troubleshoot independently
  alt Inbound cannot resolve
    IL -> SP: Request clarification
    SP -> IL: Provide clarification
  end
  IL -> CA: Provide corrected information
end

CA -> SH: Perform pickups
CA -> CA: Review BOL for obvious mistakes
CA -> IL: Email BOL copy
IL -> IL: Receive BOL

== Track & Trace ==
CA -> IL: Send load tracking template updates (Excel)
IL -> IL: Review updates (priority: loads due T+1)
alt Issues observed requiring follow-up
  IL -> CA: Email follow-up requesting clarification
  CA -> IL: Provide clarification
end

IL -> IL: Review prior-day pickups & BOL presence
alt Issue may impact supply plan
  IL -> SP: Inform supply planner
end
alt Delivery date change / load late
  IL -> ERP: Change confirmed delivery date on PO
  IL -> VH: Mark load late in "Voyage Header"
end
alt Orders not picked up OR missing BOL
  IL -> CA: Request clarification / BOL via email
  CA -> IL: Provide clarification / BOL
end

== Appointment Scheduling ==
alt Terms = FOB
  CA -> IL: Email inbound@ to request delivery appointment
else Terms = Delivered
  SH -> IL: Email inbound@ to request delivery appointment
end

IL -> IL: Review appointment request
alt Discrepancy or missing information
  IL -> SH: Email seeking clarification
  SH -> IL: Provide or seek clarification
end

IL -> WMS: Schedule appointment
WMS -> IL: Appointment confirmation
alt Requested delivery date is different
  IL -> SP: Team message informing date change
end

@enduml"""

SEQUENCE_TMS_OVERLAY = r"""@startuml

autonumber
hide footbox

actor "Supply Planner" as SP
participant "Inbound Logistics" as IL
participant "Shipper" as SH
participant "Carrier / LSP" as CA
participant "Inbound TMS API" as TMS
database  "LoadEvent Store" as EV
database  "Exception Store" as EX
database  "ExternalReference Store" as XR
database  "Cost Ledger" as CO
participant "WMS" as WMS
participant "ERP (PO System)" as ERP
participant "Voyage Header / Reporting" as VH

== Load Building & Planning ==
SP -> IL: Add order details to "Load Request File"
IL -> TMS: POST /loads (create PLANNED)
TMS -> EV: append load_created
TMS -> XR: store request_file_id

IL -> TMS: POST /loads/{id}/events (load_request_reviewed)
TMS -> EV: append load_request_reviewed

alt Missing / inaccurate info
  IL -> TMS: POST /loads/{id}/exceptions (missing_required_info)
  TMS -> EX: open missing_required_info
  IL -> SP: Request clarification
  SP -> IL: Clarification / corrections
  IL -> TMS: PATCH /loads/{id} (planning fields)
  TMS -> EV: append load_request_corrected
  IL -> TMS: PATCH /exceptions/{exId} resolved
  TMS -> EX: resolve
end

== Freight Booking ==
IL -> TMS: POST /loads/{id}/events (contract_check_completed)
TMS -> EV: append contract_check_completed

alt Contract load
  IL -> CA: Notify carrier
  IL -> TMS: POST /loads/{id}/events (carrier_notified_contract)
  TMS -> EV: append carrier_notified_contract
  IL -> TMS: POST /loads/{id}:tender
  TMS -> EV: append load_tendered
  TMS -> XR: store tender_id
else Bid load
  IL -> CA: Send bid template
  IL -> TMS: POST /loads/{id}/events (bid_template_sent)
  TMS -> EV: append bid_template_sent
  CA -> IL: Submit rates
  IL -> TMS: POST /loads/{id}/costs (expected_amount)
  TMS -> CO: append expected cost
  IL -> TMS: POST /loads/{id}/events (award_made)
  TMS -> EV: append award_made
end

== Execution / BOL ==
IL -> TMS: POST /loads/{id}:dispatch
TMS -> EV: append in_transit

CA -> IL: Send BOL
IL -> TMS: POST /external-references (bol_number)
TMS -> XR: append bol_number
IL -> TMS: POST /loads/{id}/events (bol_received)
TMS -> EV: append bol_received

== Track & Trace ==
CA -> IL: Tracking update
IL -> TMS: POST /loads/{id}/events (location_update_received)
TMS -> EV: append location_update_received

alt Late / risk
  IL -> TMS: POST /loads/{id}/exceptions (late_risk)
  TMS -> EX: open late_risk
end

== Appointment Scheduling ==
IL -> WMS: Schedule appointment
WMS -> IL: Confirmation
IL -> TMS: POST /external-references (wms_appointment_id)
TMS -> XR: append wms_appointment_id
IL -> TMS: POST /loads/{id}/events (appointment_scheduled)
TMS -> EV: append appointment_scheduled

@enduml"""


@dataclass
class Diagram:
    key: str
    title: str
    description: str
    plantuml: str


DIAGRAMS = [
    Diagram("c4_l1", "C4 L1 — System Context", "High-level actors & systems", C4_LEVEL1_CONTEXT),
    Diagram("c4_l2", "C4 L2 — Containers", "Runtime containers & integrations", C4_LEVEL2_CONTAINERS),
    Diagram("c4_l3", "C4 L3 — Refined Domain", "Core domain concepts (readable)", C4_LEVEL3_DOMAIN_REFINED),
    Diagram("uml_full", "UML — Full Domain Diagram", "Full UML with immutability markers", UML_FULL),
    Diagram("seq_current", "Sequence — Current State", "Operational flow (as-is)", SEQUENCE_CURRENT),
    Diagram("seq_overlay", "Sequence — TMS Overlay", "Operational flow + TMS recording", SEQUENCE_TMS_OVERLAY),
]


# -------------------------
# Streamlit UI
# -------------------------

st.set_page_config(page_title="Inbound TMS Diagram Explorer", layout="wide")

st.title("Inbound TMS Diagram Explorer")
st.caption("Interactive PlantUML viewer/editor for C4 layers, domain UML, and sequence diagrams.")

with st.sidebar:
    st.header("Renderer")
    server = st.selectbox(
        "PlantUML server",
        [
            "https://www.plantuml.com/plantuml",
            "https://render.powerplantuml.com/plantuml",
        ],
        help="Choose a server to render SVG/PNG. SVG is best for docs.",
    )
    fmt = st.radio("Format", ["svg", "png"], index=0)

    st.divider()
    st.header("Diagram")
    key_to_idx = {d.key: i for i, d in enumerate(DIAGRAMS)}
    chosen = st.selectbox(
        "Select",
        options=[d.key for d in DIAGRAMS],
        format_func=lambda k: next(d.title for d in DIAGRAMS if d.key == k),
    )


d = DIAGRAMS[key_to_idx[chosen]]

col_left, col_right = st.columns([0.48, 0.52], gap="large")

with col_left:
    st.subheader(d.title)
    st.write(d.description)

    st.markdown("**Edit PlantUML**")
    default_text = d.plantuml
    edited = st.text_area("", value=default_text, height=520, key=f"code_{d.key}")

    st.markdown("**Tips**")
    st.markdown(
        "- Use `skinparam Shadowing false` and more `Ranksep/Nodesep` for readability.\n"
        "- Split long sequences by phase (Planning, Booking, Execution, Trace, Scheduling).\n"
        "- Keep C4 L1 simple: actors + systems only."
    )

with col_right:
    st.subheader("Rendered")

    try:
        url = plantuml_url(server, fmt, edited)
    except Exception as e:
        st.error(f"Could not build render URL: {e}")
        url = None

    if url:
        st.markdown(f"**Render URL:** {url}")

        if fmt == "png":
            st.image(url, use_container_width=True)
        else:
            # SVG: embed so it stays crisp when zooming
            svg_html = f"""
            <div style='width:100%; height: 820px; border:1px solid #eee; overflow:auto;'>
              <object data="{url}" type="image/svg+xml" style="width:100%; height: 820px;"></object>
            </div>
            """
            st.components.v1.html(svg_html, height=860, scrolling=True)

        st.download_button(
            "Download PlantUML (.puml)",
            data=edited.encode("utf-8"),
            file_name=f"{d.key}.puml",
            mime="text/plain",
        )

st.divider()

st.header("All Layers — Quick Gallery")
st.caption("Use this to scan quickly; click a tab to open and edit.")

layer_tabs = st.tabs(["C4 L1", "C4 L2", "C4 L3", "UML", "Seq (As-Is)", "Seq (Overlay)"])

for tab, diagram_key in zip(layer_tabs, ["c4_l1", "c4_l2", "c4_l3", "uml_full", "seq_current", "seq_overlay"]):
    diag = DIAGRAMS[key_to_idx[diagram_key]]
    with tab:
        st.subheader(diag.title)
        st.caption(diag.description)
        try:
            u = plantuml_url(server, fmt, st.session_state.get(f"code_{diag.key}", diag.plantuml))
            if fmt == "png":
                st.image(u, use_container_width=True)
            else:
                st.components.v1.html(
                    f"<object data='{u}' type='image/svg+xml' style='width:100%; height: 520px; border:1px solid #eee;'></object>",
                    height=540,
                )
        except Exception as e:
            st.error(str(e))

st.info(
    "If rendering fails, try switching servers (left sidebar) or choose PNG. "
    "Some servers restrict advanced includes/macros; these diagrams avoid external includes for reliability."
)


def main() -> None:
    """Run the Streamlit app.

    This allows the repo to be installed as a package and run via a console script:
      pip install .
      inbound-tms-diagram
    """

    # Streamlit doesn't provide a simple public API for programmatic execution,
    # so we reuse the same CLI entrypoint it uses when you run `streamlit run`.
    import sys

    # When installed as a package, __file__ will point to the installed module.
    sys.argv = ["streamlit", "run", __file__]

    # The Streamlit CLI entrypoint is stable; this is the same path used by the
    # `streamlit` console script.
    import streamlit.web.cli as stcli

    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
