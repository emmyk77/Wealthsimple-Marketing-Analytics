# Rebuilding deliverables

The analytical pipeline uses requirements.txt. Run build_powerbi.py with Python 3 to regenerate the PBIP source, then check_powerbi_structure.py for offline reference and layout checks. Editing generated model/page files directly is supported, but regenerating will overwrite those edits; preserve Desktop changes in Git before regeneration.

build_report.py requires python-docx. build_deck.mjs was authored using the OpenAI artifact-tool runtime and its presentation finalization helpers; those dependencies are specific to the authoring environment and are not included in requirements.txt. The delivered DOCX/PPTX can be edited normally without that runtime. The Power BI Desktop runtime is separately required for M/DAX and final PBIX validation.
