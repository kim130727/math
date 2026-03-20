math/
├─ README.md
├─ pyproject.toml
├─ .env
├─ main.py
│
├─ assets/
│  ├─ fonts/
│  ├─ images/
│  └─ audio/
│
├─ lessons/
│  ├─ grade6_01_fraction_division.json
│  ├─ grade6_02_prism_pyramid.json
│  ├─ grade6_03_ratio.json
│  └─ ...
│
├─ templates/
│  ├─ concept_story.py
│  ├─ calculation_steps.py
│  ├─ geometry_visual.py
│  └─ graph_explainer.py
│
├─ core/
│  ├─ lesson_loader.py
│  ├─ tts_generator.py
│  ├─ timing_builder.py
│  ├─ video_builder.py
│  ├─ scene_registry.py
│  └─ utils.py
│
├─ characters/
│  ├─ character_base.py
│  ├─ jibbung.py
│  ├─ nabbung.py
│  └─ speech_bubble.py
│
├─ output/
│  ├─ grade6_01_fraction_division/
│  │  ├─ tts/
│  │  ├─ timings.json
│  │  ├─ rendered.mp4
│  │  ├─ narration_full.mp3
│  │  └─ final.mp4
│  └─ ...
│
└─ examples/
   └─ latex_test.py