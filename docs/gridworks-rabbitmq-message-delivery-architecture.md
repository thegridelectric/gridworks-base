# GridWorks Broker Message Delivery Architecture
Sema defines the shared vocabulary — the named types, enums, and formats that establish meaning across actors.

This document describes the GridWorks broker-based message delivery architecture, which specifies how Sema-typed messages are routed and transported over RabbitMQ.

Other delivery mechanisms (e.g. HTTP APIs) use the same Sema types but different transport semantics.

Axiom: Sema types are transport-independent.

## 1. Sema Types vs. Delivery

Sema types define meaning. They are transport-agnostic.

Examples:

 - `power.watts` — power measurement
 - `report.event` — batch of timestamped telemetry data

The same Sema type is identical whether transmitted via RabbitMQ, HTTP, or other mechanisms.

The broker delivery layer defines:

 - who sends and receives a message
 - how messages are routed
 - whether delivery metadata (e.g. acknowledgment) is included

This separation ensures that meaning is defined once and reused across all transports.

## 2. Message Categories

Message categories define delivery structure, not encoding and not guarantees.


**Direct (`rj`)**

Point-to-point messages between specific actors.

Use cases:
 - commands and responses
 - targeted coordination

Properties:
 - one sender to one receiver
 - no delivery tracking by default

**Broadcast (`rjb`)**

One-to-many messages sent to multiple subscribers.

Use cases:
 - market price updates
 - weather forecasts

Properties:
 - one sender to many receivers
 - optional radio channel for scoped broadcasts
 - no delivery tracking

**Wrapped (`gw`)**

Messages that include an explicit wrapper envelope with delivery metadata.

Structure:

```
{
"Header": {
"Src": "...",
"Dst": "...",
"MessageType": "...",
"MessageId": "...",
"AckRequired": false
},
"Payload": {
...
},
"TypeName": "gw"
}
```

Properties:
 - includes Header + Payload
 - supports delivery metadata such as:
  - message identity
  - optional acknowledgment requirement
  - correlation and replay tracking

Important:
 - acknowledgment is optional
 - wrapped does not imply reliable delivery

Invariant:
  - Header fields that describe routing (Src, Dst, MessageType) MUST match the routing key exactly.

**The routing key is the authoritative source of addressing.**

**Serial (future)**

Reserved for bandwidth-constrained or low-latency scenarios where JSON encoding is not appropriate.

## 3. Routing Keys

Routing keys encode the message envelope:
 - message category
 - sender GNodeAlias
 - receiver identity (if applicable)
 - Sema type

**RabbitMQ Constraints**

RabbitMQ routing keys:
 -  MUST use period . as the separator
 - MUST NOT use /
 - are tokenized by ., so each segment must be atomic
 - MUST be shorter than 256 characters (? check)

**GridWorks Transformations**

Because Sema uses left.right.dot naming for types, and similarly GNodeAliases are left.right.dot we apply the following transformations for routing keys:

Replace . with - inside identifiers:
  - GNodeAlias → hyphenated form
  - TypeName → hyphenated form


This produces a routing-safe representation sometimes referred to as a SpaceheatName-style encoding.

**Direct (`rj`)**

Pattern:

```
rj.{from-alias}.{from-class}.{type-name}.{to-class}.{to-alias}
```

Example:

```
rj.hw1-isone-me-versant-keene-spruce.ltn.bid.marketmaker.hw1-isone
```

**Broadcast (`rjb`)**

Pattern:

```
rjb.{from-alias}.{from-class}.{type-name}
```

or

```
rjb.{from-alias}.{from-class}.{type-name}.{radio-channel}
```

Examples:

```
rjb.hw1-isone-me-versant-keene.marketmaker.latest-price.rt60gate5
```

**Wrapped (`gw`)**

Pattern:

```
gw.{from-alias}.to.{to-class}.{type-name}
```

Example:

```
gw.hw1-isone-me-versant-keene-spruce-scada.to.ltn.layout-lite
```
