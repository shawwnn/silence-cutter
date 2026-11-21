# React Migration Roadmap

```mermaid
flowchart TD
    A[Approved baseline specification] --> B[Define Python bridge contract]
    B --> C[Backend reliability task]
    C --> D[React + Vite foundation]
    D --> E[Responsive UI states]
    E --> F[Bridge integration]
    F --> G[Cancellation and cleanup]
    G --> H[End-to-end verification]
    H --> I[Portfolio documentation and review]

    R[Implementation record] -. updated after each phase .-> B
    R -. updated after each phase .-> C
    R -. updated after each phase .-> D
    R -. updated after each phase .-> E
    R -. updated after each phase .-> F
    R -. updated after each phase .-> G
    R -. updated after each phase .-> H
    R -. updated after each phase .-> I

    X[Scope or architecture change] --> Y[Specification and impact review]
    Y --> Z[Approval decision]
    Z --> R
```

Current milestone: React/Vite interface, Flask bridge, accurate filter-graph exporter, synthetic timing tests, audio validation, output-duration validation, and pre-export all-content removal protection are implemented and verified by automated tests/build.

Next milestone: deploy the verified safety fix, then run the manual real-video workflow when a laptop is available. The next approved UX scope is stage-based processing feedback and a simplified workflow stepper; see `all-content-removal-specification.md`.
