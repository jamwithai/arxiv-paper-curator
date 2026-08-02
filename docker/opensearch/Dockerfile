FROM opensearchproject/opensearch:2.19.0

# analysis-icu is required for the Vietnamese analyzer (icu_tokenizer + icu_folding)
# used by the bilingual education/accounting indices (Stage 2 plan, 2b).
RUN /usr/share/opensearch/bin/opensearch-plugin install --batch analysis-icu
