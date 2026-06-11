# VE VSA Baseline Deviation Doctrine

Status: recommended doctrine update before collecting larger voice datasets.

Authority: research-informed project doctrine, not diagnosis, lie detection, medical assessment, or execution permission.

## Why This Exists

Voice-state research supports a conservative shift in Echo Root VSA language.

Speech features can change under stress, fatigue, excitement, anxiety, cognitive load, physical effort, microphone conditions, and environmental noise. Many of those conditions overlap in the same measurable features. Individual baselines also vary heavily.

Therefore, Echo Root should not frame VSA as emotion detection, stress detection, truth detection, or authority.

Use this framing instead:

```text
voice
  -> signal change
  -> personal baseline comparison
  -> possible explanations
  -> human/context review
```

## Doctrine Shift

Old mental model:

```text
voice
  -> emotion
  -> conclusion
```

New mental model:

```text
voice
  -> signal change
  -> baseline comparison
  -> possible explanations
  -> human/context review
```

The public terminology should shift from:

```text
stress detection
```

to:

```text
baseline deviation detection
```

## Priority Order

1. Speech vs noise separation
2. Intent preservation through noise
3. Deviation from a personal baseline
4. Correlation with self-reported state
5. Repeatable pattern detection

Never assume cause from voice alone.

## Baseline Categories

Do not use the first-pass labels `stressed`, `excited`, or `tired` as conclusions.

Use operator/self-report categories that stay descriptive:

| Category | Values |
| --- | --- |
| Arousal | low, medium, high |
| Fatigue | low, medium, high |
| Cognitive load | low, medium, high |
| Environmental noise | low, medium, high |
| Physical effort | resting, light, moderate, heavy |

These categories are context metadata and review aids. They are not diagnoses.

## Required Session Metadata

Every VSA sample should include:

- `speaker_id`
- `timestamp`
- `mic_device`
- `environment`
- `noise_source`
- `noise_level`
- `distance_from_microphone`
- `task_type`
- `self_reported_fatigue`
- `self_reported_stress`
- `self_reported_focus`
- `physical_effort`
- `consent_status`

If consent is absent or unclear, do not collect or promote the sample.

## Environment Ladder

Do not start with chaos. Build signal degradation curves gradually.

| Stage | Environment |
| --- | --- |
| 0 | Quiet room baseline |
| 1 | HVAC or fan |
| 2 | TV low volume |
| 3 | Music low volume |
| 4 | People talking |
| 5 | Random intermittent sounds |
| 6 | Mixed noise environment |

Each stage should preserve metadata, self-report, and consent state.

## Features To Track Later

Track measurable speech features such as:

- pitch centroid
- pitch range
- tempo
- pause rate
- jitter
- shimmer
- energy
- speech ratio

Prioritize personal baseline drift over generic emotional classification.

The most useful comparison is often:

```text
Current speaker
  vs
Baseline speaker
```

not:

```text
Speaker
  vs
Average human
```

## Echo Root Principle

```text
VSA signal != diagnosis
VSA signal != authority
VSA signal != truth

VSA signal = context evidence
```

## Success Metric

Do not ask:

```text
Did we detect stress?
```

Ask:

```text
Did we accurately detect a deviation from this person's baseline?
```

That question is more measurable, more defensible, and less likely to drift into voice lie-detector claims.

## Collection Gate

Before collecting VSA samples, require:

1. Clear consent for recording/storage.
2. Speaker identity or anonymized speaker id.
3. Baseline stage and environment metadata.
4. Self-report fields.
5. A statement that no diagnosis, deception inference, or authority decision will be made from voice alone.

## Research Notes

- Van Puyvelde et al., "Voice Stress Analysis: A New Framework for Voice and Effort in Human Performance," Frontiers in Psychology, 2018, reviews speech changes across physical load, performance-impacting conditions, emotional load, cognitive load, and mixed load contexts: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.01994/full
- The National Institute of Justice report "Investigation and Evaluation of Voice Stress Analysis Technology" is a cautionary source for avoiding deception/lie-detector overclaims: https://www.ojp.gov/pdffiles1/nij/193832.pdf

## Short Operator Reminder

```text
Old question:
What emotion is this?

Better question:
What changed?

Best question:
What changed compared to this person's normal baseline?
```
