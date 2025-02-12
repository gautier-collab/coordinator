<template>
    <b-card-body style="padding: 0;">
        <b-row class="textmining-paginator">
            <b-col>
                <expander v-model="isSearchParamsVisible" />&nbsp;
                <b>Results:</b>&nbsp;
                <span v-if="loadingVariomes">
                    <b-spinner small /> loading...
                </span>
                <span v-else>{{ totalRows && totalRows.toLocaleString() }}</span>
            </b-col>
            <b-col class="my-1">
                <b-form-group label="Per page" label-cols-sm="6" label-cols-md="4" label-cols-lg="3" label-align-sm="right" label-size="sm" label-for="perPageSelect" class="mb-0">
                    <b-form-select v-model="perPage" id="perPageSelect" size="sm" :options="pageOptions"/>
                </b-form-group>
            </b-col>

            <b-col class="my-1 pager-search">
                <b-pagination v-model="currentPage" :total-rows="totalRows" :per-page="perPage" align="fill" size="sm" class="my-0"/>
            </b-col>

            <b-col>
                <b-input-group size="sm">
                    <b-form-input v-model="search" debounce="300" placeholder="Type to Search"/>
                    <b-input-group-append>
                        <b-btn :disabled="!search" @click="search = ''">Clear</b-btn>
                    </b-input-group-append>
                </b-input-group>
            </b-col>

            <b-col class="my-1 pager-search" md="2">
                <b-select v-model="filterCollection">
                    <b-select-option :value="null">---</b-select-option>
                    <b-select-option :value="'medline'">medline</b-select-option>
                    <b-select-option :value="'pmc'">PMC</b-select-option>
                </b-select>
            </b-col>
        </b-row>

        <b-collapse :visible="isSearchParamsVisible">
            <b-row class="search-params" align-v="center">
                <b-col class="d-inline-flex align-items-center">
                    <b>Disease:</b>
                    <v-select style="background: white; width: 450px; margin-left: 10px;" v-model="disease" placeholder="select a disease to query"
                        :options="pub_diseases" label="name" :clearable="true"
                    >
                        <template v-slot:option="option">
                            <div style="display: flex; justify-content: space-between; margin: 5px;">
                                <div style="flex: 1 1;">{{ option.name }}</div>
                                <div style="font-style: italic; color: #777; font-size: smaller;">{{ option.count }}</div>
                            </div>
                        </template>
                    </v-select>
                </b-col>

                <!--
                <b-col cols="auto">
                    <b-button size="sm" variant="info" :disabled="loadingVariomes" @click="query" style="margin-bottom: 2px;">
                        <icon name="search" /> Query
                    </b-button>
                </b-col>
                -->
            </b-row>
        </b-collapse>


        <div style="margin-top: 10px;">
            <div v-if="variomesError" class="text-center text-muted font-italic">
                <icon name="exclamation-triangle" scale="3" style="vertical-align: text-bottom; margin-bottom: 5px;" /><br />
                {{ variomesError.message }}<br />
                ({{ variomesError.reason }})
            </div>
            <b-table v-else show-empty :busy="variomes.length === 0"
                primary-key="id"
                :fields="fieldsTextMining" :items="pubs_by_disease" thead-class="unwrappable-header"
                :sort-by="sortBy" :sort-desc="sortDesc"
                :filter="search"
                :current-page="currentPage" :per-page="perPage" small
            >
                <template v-slot:table-busy>
                    <div class="text-center text-danger my-2">
                        <b-spinner class="align-middle" small style="margin-right: 5px;" />
                        <strong>Loading...</strong>
                    </div>
                </template>

                <template v-slot:cell(expando)="row">
                    <row-expander :row="row" />
                </template>

                <template v-slot:cell(id)="row">
                    <VariomesLitPopover
                        :pubmeta="{ pmid: row.item.id }"
                        :variant="preferredTerms.variant"
                        :gene="preferredTerms.gene"
                        :disease="preferredTerms.disease"
                        deferred
                    />
                </template>
                <template v-slot:cell(title_highlight)="data">
                    <span v-html="data.value"></span>
                </template>

                <template v-slot:cell(action)="row">
                    <pass :used_ref="annotationUsed(source, row.item.id)">
                        <span slot-scope="{ used_ref }">
                            <b-button
                                :ref="`add_btn_${row.item.id}`"
                                :variant="used_ref ? 'warning' : 'success'"
                                size="sm"
                                @click="addEvidenceFromList(row.item.id)"
                                target="_blank"
                            >
                                <icon name="plus" />
                            </b-button>
                            <b-popover v-if="used_ref"
                                :target="() => $refs[`add_btn_${row.item.id}`]"
                                triggers="hover focus"
                                data-container="body"
                            >
                                <template v-slot:title>
                                    <div class="d-flex align-items-center">
                                        <icon name="exclamation-triangle" scale="1.1" class="mr-1 mt-1" />
                                        <div>Reference in Use</div>
                                    </div>
                                </template>
                                <template>
                                This reference is already in use by:
                                <EntriesInUse :annotation-used="used_ref" />
                                </template>
                            </b-popover>
                        </span>
                    </pass>
                </template>

                <template v-slot:cell(authors)="data">{{ data.value && data.value.join(", ") }}</template>
                <template v-slot:cell(publication_types)="data">
                    <b class="mb-1 d-block">{{ data.item.collection }}</b>
                    {{ data.value && data.value.join(", ") }}<br />
                </template>
                <template v-slot:cell(score)="data">
                    <b class="dotted-line" :ref="data.item.id">{{ data.value.toFixed(2) }}</b>
                    <b-tooltip :target="() => $refs[data.item.id]">
                        <pass :querydetails="data.item.details.query_details">
                            <ul slot-scope="{ querydetails }" v-if="querydetails" class="p-0 m-0">
                                <li v-if="querydetails.query_gene_count" class="d-flex justify-content-between align-items-center gene">
                                    {{preferredTerms.gene}}
                                    <span class="text-white pl-1">{{querydetails.query_gene_count.all}}</span>
                                </li>
                                <li v-if="querydetails.query_variant_count" class="d-flex justify-content-between align-items-center variant">
                                    {{preferredTerms.variant}}
                                    <span class="text-white pl-1">{{querydetails.query_variant_count.all}}</span>
                                </li>
                                <li v-if="preferredTerms.disease && preferredTerms.disease !== 'none' && querydetails.query_disease_count" class="d-flex justify-content-between align-items-center disease">
                                    {{preferredTerms.disease}}
                                    <span class="text-white pl-1">{{querydetails.query_disease_count.all}}</span>
                                </li>
                            </ul>
                            <span v-else>count data unavailable</span>
                        </pass>
                    </b-tooltip>
                </template>

                <template v-slot:row-details="data">
                    <TransitionExpand>
                        <div v-if="data.item._showDetails" class="sample-subtable tumor-subtable">
                            <h5>Facets</h5>

                            <ul>
                                <li v-for="(data, facet_name) in data.item.details.facet_details" :key="facet_name">
                                    <b>{{ facet_name }}</b>
                                    <ul>
                                        <li v-for="(entry, idx) in data" :key="idx">
                                            {{ entry.preferred_term }}
                                            <i v-if="entry.count">({{ entry.count }})</i>
                                        </li>
                                    </ul>
                                </li>
                            </ul>
                        </div>
                    </TransitionExpand>
                </template>
            </b-table>
        </div>

        <b-row>
            <b-col>
                <b-alert show variant="info" class="d-flex align-items-center justify-content-between mb-0">
                    <icon name="star" style="flex: 0 1;" class="mr-1" />
                    <div class="d-flex align-items-center">
                        For multi-variant search, batch querying, and many other features, see the official interface:
                        <a class="ml-1" href="https://candy.hesge.ch/Variomes/" target="_blank">Variomes</a>
                        <icon class="ml-1" name="external-link-alt" />
                    </div>
                    <icon name="star" style="flex: 0 1;" />
                </b-alert>
            </b-col>
        </b-row>
    </b-card-body>
</template>

<script>
import VariomesLitPopover from "@/components/widgets/VariomesLitPopover";
import fieldsTextMining from "@/data/curation/text_mining/fields.json";
import { desnakify } from "@/utils";
import { HTTP } from "@/router/http";
import TransitionExpand from "@/components/widgets/TransitionExpand";
import EntriesInUse from "@/components/widgets/curation/AnnotationsInUse";

export default {
    name: "VariomesSearch",
    components: {
        EntriesInUse,
        VariomesLitPopover,
        TransitionExpand
    },
    props: {
        variant: { type: Object, required: true },
        gene: { type: Object, required: true },
        used_references: { type: Object }
    },
    data() {
        return {
            fieldsTextMining,
            source: "PMID",
            collections: ["pmc","medline"],
            filterCollection: null,
            reference: null,
            variomes: [],
            loadingVariomes: true,
            variomesError: null,
            totalRows: 0,
            sortBy: "score",
            sortDesc: true,
            currentPage: 1,
            perPage: 10,
            pageOptions: [10, 20, 30],

            isSearchParamsVisible: false,
            disease: null,
            diseases: [],
            search: ''
        };
    },
    computed: {
        disease_id() {
            return parseInt(this.$route.params.disease_id);
        },
        combinedPubs() {
            if (!this.variomes || !this.variomes.publications)
                return [];

            if (this.filterCollection) {
                return this.variomes.publications[this.filterCollection];
            }

            // concatenates and returns all subkeys of 'publications', e.g. 'medline', 'pmc'
            return Object.values(this.variomes.publications).reduce((acc, x) => acc.concat(x), []);
        },
        preferredTerms() {
            if (!this.variomes || !this.variomes.normalized_query)
                return {};

            const nq = this.variomes.normalized_query;

            return {
                gene: nq.genes && nq.genes.length > 0  && (nq.genes[0].preferred_term || nq.genes[0].query_term),
                variant: nq.variants && nq.variants.length > 0  && (nq.variants[0].preferred_term || nq.variants[0].query_term),
                disease: nq.diseases && nq.diseases.length > 0  && (nq.diseases[0].preferred_term || nq.diseases[0].query_term),
            }
        },
        /**
         * Gets the set of diseases mentioned in all returned publications, with the number of times it's been found in a publication.
         * @return {null|[{name: String, count: Number}]}
         */
        pub_diseases() {
            const disease_map = this.combinedPubs.reduce((diseases, pub) => {
                // record each disease and the number of publications that feature it
                if (pub.details.facet_details.diseases) {
                    const disease_names = pub.details.facet_details.diseases.map(x => x.preferred_term);
                    disease_names.forEach(x => {
                        if (diseases[x] !== undefined) { diseases[x] += 1; }
                        else { diseases[x] = 1; }
                    });
                }
                return diseases;
            }, {});

            return Object.entries(disease_map)
                .map(([name, count]) => ({ name, count }))
                .sort((a, b) => b.count - a.count);
        },
        pubs_by_disease() {
            if (!this.disease)
                return this.combinedPubs;

            return this.combinedPubs
                .filter(pub => pub.details.facet_details.diseases.some(y => y.preferred_term === this.disease.name));
        }
    },
    // components: {geneVariants: geneVariants},
    methods: {
        desnakify,
        addEvidenceFromList(id) {
            this.$emit('add-evidence-from-list', id);
        },
        query() {
            this.loadingVariomes = true;
            this.variomesError = null;
            HTTP.get(`variomes_search`, {
                params: {
                    genvars: `${this.variant.gene.symbol} (${this.variant.name})`,
                    disease: this.disease && this.disease.name,
                    collection: this.collections.join(",")
                }
            })
                .then(response => {
                    this.variomes = response.data;
                    this.totalRows = this.combinedPubs.length;
                })
                .catch(err => {
                    this.variomesError = {
                        message: "Couldn't retrieve publication info, try again later.",
                        reason: err
                    };
                })
                .finally(() => { this.loadingVariomes = false; });
        },
        annotationUsed(source, reference) {
            if (!source || !reference || !this.used_references) {
                return null;
            }

            return this.used_references[`${source.trim()}:${reference.trim()}`];
        }
    },
    async created() {
        // const { disease_id } = this.$route.params;

        // first, get all the diseases
        this.icdo_diseases = await HTTP.get(`/diseases?page_size=9999`).then(response => response.data.results);
        // preselect the one we found
        // this.disease = disease_id && this.diseases.find(x => x.id == disease_id);

        // then, query variomes based on that data
        this.query();

        // TODO: decide if we should populate the disease dropdown with what's actually returned
        //  (it'd be nice, but we'll need to scan the query for all diseases before we do it)
    }
};
</script>

<style scoped>
.textmining-paginator {
    border-bottom: solid 1px #ddd; padding-bottom: 10px; display: flex; align-items: baseline;
}

.search-params {
    padding: 10px;
    border-bottom: solid 1px #ddd; display: flex; align-items: baseline;
    background: #eee;
}

.pager-search {
    display: flex;
    flex-direction: row;
    align-items: center;
}
.pager-search .pagination {
    flex: 1 0;
    margin-right: 5px;
}

.gene {color: #e3639f;font-weight: bold;}
.variant {color: #4b7bef;font-weight: bold;}
.disease {color: #3d811e;font-weight: bold;}
</style>
