# VSA Tuning Round 1

Goal: prepare the first voice-signal tuning pass around baseline deviation
detection, not emotion detection.

This checklist is for controlled local collection and review. It is not medical
assessment, lie detection, identity proof, gender inference, or authority.

## Doctrine

- Voice signal is context evidence.
- Voice signal is not diagnosis.
- Voice signal is not truth.
- Voice signal is not permission.
- Baseline deviation is the target, not emotion classification.
- Speaker-specific comparison is more useful than average-human comparison.

## Round 1 Question

Do not ask:

```text
What emotion is this?
```

Ask:

```text
What changed compared to this speaker's own baseline?
```

## Speaker Setup

Create a separate baseline profile for each consenting speaker.

Minimum fields:

- `speaker_id`
- `display_name`
- `consent_status`
- `recording_scope`
- `mic_device`
- `usual_distance_from_microphone`
- `preferred_language`
- `known_voice_notes`
- `baseline_created_at`

Optional calibration metadata:

- `self_reported_voice_register`: low, medium, high, variable
- `self_reported_sex_or_gender_context`: optional, self-reported, not inferred
- `pitch_range_notes`: optional, measured after baseline collection
- `tone_notes`: optional, descriptive, not diagnostic

Do not infer sex, gender, identity, deception, stress, or emotional state from
voice alone.

## Round 1 Speakers

Initial useful comparisons:

- Richard vs baseline Richard
- Ashley vs baseline Ashley
- Richard current vs Richard baseline
- Ashley current vs Ashley baseline

Avoid treating this as:

- Richard vs average male
- Ashley vs average female
- male vs female authority
- male vs male identity proof
- voice match as consent

Male/female or voice-register notes can help calibrate expected pitch ranges,
but the gate should still compare the current sample to that speaker's own
baseline first.

## Collection Ladder

Collect gradually:

| Stage | Environment |
| --- | --- |
| 0 | Quiet room baseline |
| 1 | HVAC or fan |
| 2 | TV low volume |
| 3 | Music low volume |
| 4 | People talking |
| 5 | Random intermittent sounds |
| 6 | Mixed noise environment |

Stop if consent becomes unclear or the speaker requests a pause.

## Sample Metadata

Each sample should record:

- `sample_id`
- `speaker_id`
- `timestamp`
- `mic_device`
- `environment_stage`
- `noise_source`
- `noise_level`
- `distance_from_microphone`
- `task_type`
- `script_or_prompt_id`
- `self_reported_arousal`
- `self_reported_fatigue`
- `self_reported_cognitive_load`
- `self_reported_stress`
- `self_reported_focus`
- `physical_effort`
- `consent_status`

## Features To Track

Start with measurable features:

- pitch centroid
- pitch range
- tempo
- pause rate
- jitter
- shimmer
- energy
- speech ratio

Keep feature extraction separate from interpretation.

## Gate Conditions

`PROCEED` with collection only when:

- consent is clear
- speaker profile exists
- environment stage is recorded
- mic/device metadata is recorded
- sample purpose is bounded

`PAUSE` when:

- consent is unclear
- speaker profile is missing
- environment metadata is missing
- device changed unexpectedly
- noise stage is too high for current ladder step
- self-report fields are missing

`ABORT` when:

- speaker declines recording
- sample is being used for diagnosis, deception, or authority
- sample would be promoted without review
- identity/scope conflict exists

`SAFE_MODE` when:

- consent ledger is broken
- baseline chain is corrupted
- samples are mixed across speakers
- route fallback changes storage or processing path unsafely

## Round 1 Success Metric

Success is:

```text
We can detect and explain a measurable deviation from this speaker's own
baseline under known metadata conditions.
```

Failure is:

```text
We claim stress, truth, diagnosis, identity, consent, or authority from voice
alone.
```
