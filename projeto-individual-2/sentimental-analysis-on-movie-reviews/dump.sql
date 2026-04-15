--
-- PostgreSQL database dump
--

\restrict ZEmC1pns6SIX2XrKjgvmjzyWF8FrxygF8xe08ttffIWLlofXFUh1ewJuaeGFdgN

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg13+1)
-- Dumped by pg_dump version 15.17 (Debian 15.17-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: prevent_secrets_aad_mutation(); Type: FUNCTION; Schema: public; Owner: mlflow
--

CREATE FUNCTION public.prevent_secrets_aad_mutation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF OLD.secret_id != NEW.secret_id OR OLD.secret_name != NEW.secret_name THEN
        RAISE EXCEPTION 'secret_id and secret_name are immutable (used as AAD in encryption)';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.prevent_secrets_aad_mutation() OWNER TO mlflow;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO mlflow;

--
-- Name: assessments; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.assessments (
    assessment_id character varying(50) NOT NULL,
    trace_id character varying(50) NOT NULL,
    name character varying(250) NOT NULL,
    assessment_type character varying(20) NOT NULL,
    value text NOT NULL,
    error text,
    created_timestamp bigint NOT NULL,
    last_updated_timestamp bigint NOT NULL,
    source_type character varying(50) NOT NULL,
    source_id character varying(250),
    run_id character varying(32),
    span_id character varying(50),
    rationale text,
    overrides character varying(50),
    valid boolean NOT NULL,
    assessment_metadata text
);


ALTER TABLE public.assessments OWNER TO mlflow;

--
-- Name: budget_policies; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.budget_policies (
    budget_policy_id character varying(36) NOT NULL,
    budget_unit character varying(32) NOT NULL,
    budget_amount double precision NOT NULL,
    duration_unit character varying(32) NOT NULL,
    duration_value integer NOT NULL,
    target_scope character varying(32) NOT NULL,
    budget_action character varying(32) NOT NULL,
    created_by character varying(255),
    created_at bigint NOT NULL,
    last_updated_by character varying(255),
    last_updated_at bigint NOT NULL,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.budget_policies OWNER TO mlflow;

--
-- Name: datasets; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.datasets (
    dataset_uuid character varying(36) NOT NULL,
    experiment_id integer NOT NULL,
    name character varying(500) NOT NULL,
    digest character varying(36) NOT NULL,
    dataset_source_type character varying(36) NOT NULL,
    dataset_source text NOT NULL,
    dataset_schema text,
    dataset_profile text
);


ALTER TABLE public.datasets OWNER TO mlflow;

--
-- Name: endpoint_bindings; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.endpoint_bindings (
    endpoint_id character varying(36) NOT NULL,
    resource_type character varying(50) NOT NULL,
    resource_id character varying(255) NOT NULL,
    created_at bigint NOT NULL,
    created_by character varying(255),
    last_updated_at bigint NOT NULL,
    last_updated_by character varying(255),
    display_name character varying(255)
);


ALTER TABLE public.endpoint_bindings OWNER TO mlflow;

--
-- Name: endpoint_model_mappings; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.endpoint_model_mappings (
    mapping_id character varying(36) NOT NULL,
    endpoint_id character varying(36) NOT NULL,
    model_definition_id character varying(36) NOT NULL,
    weight double precision NOT NULL,
    created_by character varying(255),
    created_at bigint NOT NULL,
    linkage_type character varying(64) DEFAULT 'PRIMARY'::character varying NOT NULL,
    fallback_order integer
);


ALTER TABLE public.endpoint_model_mappings OWNER TO mlflow;

--
-- Name: endpoint_tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.endpoint_tags (
    key character varying(250) NOT NULL,
    value character varying(5000),
    endpoint_id character varying(36) NOT NULL
);


ALTER TABLE public.endpoint_tags OWNER TO mlflow;

--
-- Name: endpoints; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.endpoints (
    endpoint_id character varying(36) NOT NULL,
    name character varying(255),
    created_by character varying(255),
    created_at bigint NOT NULL,
    last_updated_by character varying(255),
    last_updated_at bigint NOT NULL,
    routing_strategy character varying(64),
    fallback_config_json text,
    experiment_id integer,
    usage_tracking boolean DEFAULT false NOT NULL,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.endpoints OWNER TO mlflow;

--
-- Name: entity_associations; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.entity_associations (
    association_id character varying(36) NOT NULL,
    source_type character varying(36) NOT NULL,
    source_id character varying(36) NOT NULL,
    destination_type character varying(36) NOT NULL,
    destination_id character varying(36) NOT NULL,
    created_time bigint
);


ALTER TABLE public.entity_associations OWNER TO mlflow;

--
-- Name: evaluation_dataset_records; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.evaluation_dataset_records (
    dataset_record_id character varying(36) NOT NULL,
    dataset_id character varying(36) NOT NULL,
    inputs json NOT NULL,
    expectations json,
    tags json,
    source json,
    source_id character varying(36),
    source_type character varying(255),
    created_time bigint,
    last_update_time bigint,
    created_by character varying(255),
    last_updated_by character varying(255),
    input_hash character varying(64) NOT NULL,
    outputs json
);


ALTER TABLE public.evaluation_dataset_records OWNER TO mlflow;

--
-- Name: evaluation_dataset_tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.evaluation_dataset_tags (
    dataset_id character varying(36) NOT NULL,
    key character varying(255) NOT NULL,
    value character varying(5000)
);


ALTER TABLE public.evaluation_dataset_tags OWNER TO mlflow;

--
-- Name: evaluation_datasets; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.evaluation_datasets (
    dataset_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    schema text,
    profile text,
    digest character varying(64),
    created_time bigint,
    last_update_time bigint,
    created_by character varying(255),
    last_updated_by character varying(255),
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.evaluation_datasets OWNER TO mlflow;

--
-- Name: experiment_tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.experiment_tags (
    key character varying(250) NOT NULL,
    value character varying(5000),
    experiment_id integer NOT NULL
);


ALTER TABLE public.experiment_tags OWNER TO mlflow;

--
-- Name: experiments; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.experiments (
    experiment_id integer NOT NULL,
    name character varying(256) NOT NULL,
    artifact_location character varying(256),
    lifecycle_stage character varying(32),
    creation_time bigint,
    last_update_time bigint,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL,
    CONSTRAINT experiments_lifecycle_stage CHECK (((lifecycle_stage)::text = ANY ((ARRAY['active'::character varying, 'deleted'::character varying])::text[])))
);


ALTER TABLE public.experiments OWNER TO mlflow;

--
-- Name: experiments_experiment_id_seq; Type: SEQUENCE; Schema: public; Owner: mlflow
--

CREATE SEQUENCE public.experiments_experiment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.experiments_experiment_id_seq OWNER TO mlflow;

--
-- Name: experiments_experiment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mlflow
--

ALTER SEQUENCE public.experiments_experiment_id_seq OWNED BY public.experiments.experiment_id;


--
-- Name: input_tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.input_tags (
    input_uuid character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value character varying(500) NOT NULL
);


ALTER TABLE public.input_tags OWNER TO mlflow;

--
-- Name: inputs; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.inputs (
    input_uuid character varying(36) NOT NULL,
    source_type character varying(36) NOT NULL,
    source_id character varying(36) NOT NULL,
    destination_type character varying(36) NOT NULL,
    destination_id character varying(36) NOT NULL,
    step bigint DEFAULT '0'::bigint NOT NULL
);


ALTER TABLE public.inputs OWNER TO mlflow;

--
-- Name: issues; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.issues (
    issue_id character varying(36) NOT NULL,
    experiment_id integer NOT NULL,
    name character varying(250) NOT NULL,
    description text NOT NULL,
    status character varying(50) NOT NULL,
    severity character varying(50),
    root_causes text,
    source_run_id character varying(32),
    categories text,
    created_timestamp bigint NOT NULL,
    last_updated_timestamp bigint NOT NULL,
    created_by character varying(255)
);


ALTER TABLE public.issues OWNER TO mlflow;

--
-- Name: jobs; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.jobs (
    id character varying(36) NOT NULL,
    creation_time bigint NOT NULL,
    job_name character varying(500) NOT NULL,
    params text NOT NULL,
    timeout double precision,
    status integer NOT NULL,
    result text,
    retry_count integer NOT NULL,
    last_update_time bigint NOT NULL,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL,
    status_details json
);


ALTER TABLE public.jobs OWNER TO mlflow;

--
-- Name: latest_metrics; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.latest_metrics (
    key character varying(250) NOT NULL,
    value double precision NOT NULL,
    "timestamp" bigint,
    step bigint NOT NULL,
    is_nan boolean NOT NULL,
    run_uuid character varying(32) NOT NULL
);


ALTER TABLE public.latest_metrics OWNER TO mlflow;

--
-- Name: logged_model_metrics; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.logged_model_metrics (
    model_id character varying(36) NOT NULL,
    metric_name character varying(500) NOT NULL,
    metric_timestamp_ms bigint NOT NULL,
    metric_step bigint NOT NULL,
    metric_value double precision,
    experiment_id integer NOT NULL,
    run_id character varying(32) NOT NULL,
    dataset_uuid character varying(36),
    dataset_name character varying(500),
    dataset_digest character varying(36)
);


ALTER TABLE public.logged_model_metrics OWNER TO mlflow;

--
-- Name: logged_model_params; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.logged_model_params (
    model_id character varying(36) NOT NULL,
    experiment_id integer NOT NULL,
    param_key character varying(255) NOT NULL,
    param_value text NOT NULL
);


ALTER TABLE public.logged_model_params OWNER TO mlflow;

--
-- Name: logged_model_tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.logged_model_tags (
    model_id character varying(36) NOT NULL,
    experiment_id integer NOT NULL,
    tag_key character varying(255) NOT NULL,
    tag_value text NOT NULL
);


ALTER TABLE public.logged_model_tags OWNER TO mlflow;

--
-- Name: logged_models; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.logged_models (
    model_id character varying(36) NOT NULL,
    experiment_id integer NOT NULL,
    name character varying(500) NOT NULL,
    artifact_location character varying(1000) NOT NULL,
    creation_timestamp_ms bigint NOT NULL,
    last_updated_timestamp_ms bigint NOT NULL,
    status integer NOT NULL,
    lifecycle_stage character varying(32),
    model_type character varying(500),
    source_run_id character varying(32),
    status_message character varying(1000),
    CONSTRAINT logged_models_lifecycle_stage_check CHECK (((lifecycle_stage)::text = ANY ((ARRAY['active'::character varying, 'deleted'::character varying])::text[])))
);


ALTER TABLE public.logged_models OWNER TO mlflow;

--
-- Name: metrics; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.metrics (
    key character varying(250) NOT NULL,
    value double precision NOT NULL,
    "timestamp" bigint NOT NULL,
    run_uuid character varying(32) NOT NULL,
    step bigint DEFAULT '0'::bigint NOT NULL,
    is_nan boolean DEFAULT false NOT NULL
);


ALTER TABLE public.metrics OWNER TO mlflow;

--
-- Name: model_definitions; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.model_definitions (
    model_definition_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    secret_id character varying(36),
    provider character varying(64) NOT NULL,
    model_name character varying(256) NOT NULL,
    created_by character varying(255),
    created_at bigint NOT NULL,
    last_updated_by character varying(255),
    last_updated_at bigint NOT NULL,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.model_definitions OWNER TO mlflow;

--
-- Name: model_version_tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.model_version_tags (
    key character varying(250) NOT NULL,
    value text,
    name character varying(256) NOT NULL,
    version integer NOT NULL,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.model_version_tags OWNER TO mlflow;

--
-- Name: model_versions; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.model_versions (
    name character varying(256) NOT NULL,
    version integer NOT NULL,
    creation_time bigint,
    last_updated_time bigint,
    description character varying(5000),
    user_id character varying(256),
    current_stage character varying(20),
    source character varying(500),
    run_id character varying(32),
    status character varying(20),
    status_message character varying(500),
    run_link character varying(500),
    storage_location character varying(500),
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.model_versions OWNER TO mlflow;

--
-- Name: online_scoring_configs; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.online_scoring_configs (
    online_scoring_config_id character varying(36) NOT NULL,
    scorer_id character varying(36) NOT NULL,
    sample_rate double precision NOT NULL,
    experiment_id integer NOT NULL,
    filter_string text
);


ALTER TABLE public.online_scoring_configs OWNER TO mlflow;

--
-- Name: params; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.params (
    key character varying(250) NOT NULL,
    value character varying(8000) NOT NULL,
    run_uuid character varying(32) NOT NULL
);


ALTER TABLE public.params OWNER TO mlflow;

--
-- Name: registered_model_aliases; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.registered_model_aliases (
    alias character varying(256) NOT NULL,
    version integer NOT NULL,
    name character varying(256) NOT NULL,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.registered_model_aliases OWNER TO mlflow;

--
-- Name: registered_model_tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.registered_model_tags (
    key character varying(250) NOT NULL,
    value character varying(5000),
    name character varying(256) NOT NULL,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.registered_model_tags OWNER TO mlflow;

--
-- Name: registered_models; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.registered_models (
    name character varying(256) NOT NULL,
    creation_time bigint,
    last_updated_time bigint,
    description character varying(5000),
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.registered_models OWNER TO mlflow;

--
-- Name: runs; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.runs (
    run_uuid character varying(32) NOT NULL,
    name character varying(250),
    source_type character varying(20),
    source_name character varying(500),
    entry_point_name character varying(50),
    user_id character varying(256),
    status character varying(9),
    start_time bigint,
    end_time bigint,
    source_version character varying(50),
    lifecycle_stage character varying(20),
    artifact_uri character varying(200),
    experiment_id integer,
    deleted_time bigint,
    CONSTRAINT runs_lifecycle_stage CHECK (((lifecycle_stage)::text = ANY ((ARRAY['active'::character varying, 'deleted'::character varying])::text[]))),
    CONSTRAINT runs_status_check CHECK (((status)::text = ANY ((ARRAY['SCHEDULED'::character varying, 'FAILED'::character varying, 'FINISHED'::character varying, 'RUNNING'::character varying, 'KILLED'::character varying])::text[]))),
    CONSTRAINT source_type CHECK (((source_type)::text = ANY ((ARRAY['NOTEBOOK'::character varying, 'JOB'::character varying, 'LOCAL'::character varying, 'UNKNOWN'::character varying, 'PROJECT'::character varying])::text[])))
);


ALTER TABLE public.runs OWNER TO mlflow;

--
-- Name: scorer_versions; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.scorer_versions (
    scorer_id character varying(36) NOT NULL,
    scorer_version integer NOT NULL,
    serialized_scorer text NOT NULL,
    creation_time bigint
);


ALTER TABLE public.scorer_versions OWNER TO mlflow;

--
-- Name: scorers; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.scorers (
    experiment_id integer NOT NULL,
    scorer_name character varying(256) NOT NULL,
    scorer_id character varying(36) NOT NULL
);


ALTER TABLE public.scorers OWNER TO mlflow;

--
-- Name: secrets; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.secrets (
    secret_id character varying(36) NOT NULL,
    secret_name character varying(255) NOT NULL,
    encrypted_value bytea NOT NULL,
    wrapped_dek bytea NOT NULL,
    kek_version integer NOT NULL,
    masked_value character varying(500) NOT NULL,
    provider character varying(64),
    auth_config text,
    description text,
    created_by character varying(255),
    created_at bigint NOT NULL,
    last_updated_by character varying(255),
    last_updated_at bigint NOT NULL,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.secrets OWNER TO mlflow;

--
-- Name: span_metrics; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.span_metrics (
    trace_id character varying(50) NOT NULL,
    span_id character varying(50) NOT NULL,
    key character varying(250) NOT NULL,
    value double precision
);


ALTER TABLE public.span_metrics OWNER TO mlflow;

--
-- Name: spans; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.spans (
    trace_id character varying(50) NOT NULL,
    experiment_id integer NOT NULL,
    span_id character varying(50) NOT NULL,
    parent_span_id character varying(50),
    name text,
    type character varying(500),
    status character varying(50) NOT NULL,
    start_time_unix_nano bigint NOT NULL,
    end_time_unix_nano bigint,
    duration_ns bigint GENERATED ALWAYS AS ((end_time_unix_nano - start_time_unix_nano)) STORED,
    content text NOT NULL,
    dimension_attributes json
);


ALTER TABLE public.spans OWNER TO mlflow;

--
-- Name: tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.tags (
    key character varying(250) NOT NULL,
    value character varying(8000),
    run_uuid character varying(32) NOT NULL
);


ALTER TABLE public.tags OWNER TO mlflow;

--
-- Name: trace_info; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.trace_info (
    request_id character varying(50) NOT NULL,
    experiment_id integer NOT NULL,
    timestamp_ms bigint NOT NULL,
    execution_time_ms bigint,
    status character varying(50) NOT NULL,
    client_request_id character varying(50),
    request_preview character varying(1000),
    response_preview character varying(1000)
);


ALTER TABLE public.trace_info OWNER TO mlflow;

--
-- Name: trace_metrics; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.trace_metrics (
    request_id character varying(50) NOT NULL,
    key character varying(250) NOT NULL,
    value double precision
);


ALTER TABLE public.trace_metrics OWNER TO mlflow;

--
-- Name: trace_request_metadata; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.trace_request_metadata (
    key character varying(250) NOT NULL,
    value character varying(8000),
    request_id character varying(50) NOT NULL
);


ALTER TABLE public.trace_request_metadata OWNER TO mlflow;

--
-- Name: trace_tags; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.trace_tags (
    key character varying(250) NOT NULL,
    value character varying(8000),
    request_id character varying(50) NOT NULL
);


ALTER TABLE public.trace_tags OWNER TO mlflow;

--
-- Name: webhook_events; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.webhook_events (
    webhook_id character varying(256) NOT NULL,
    entity character varying(50) NOT NULL,
    action character varying(50) NOT NULL
);


ALTER TABLE public.webhook_events OWNER TO mlflow;

--
-- Name: webhooks; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.webhooks (
    webhook_id character varying(256) NOT NULL,
    name character varying(256) NOT NULL,
    description character varying(1000),
    url character varying(500) NOT NULL,
    status character varying(20) DEFAULT 'ACTIVE'::character varying NOT NULL,
    secret character varying(1000),
    creation_timestamp bigint,
    last_updated_timestamp bigint,
    deleted_timestamp bigint,
    workspace character varying(63) DEFAULT 'default'::character varying NOT NULL
);


ALTER TABLE public.webhooks OWNER TO mlflow;

--
-- Name: workspaces; Type: TABLE; Schema: public; Owner: mlflow
--

CREATE TABLE public.workspaces (
    name character varying(63) NOT NULL,
    description text,
    default_artifact_root text
);


ALTER TABLE public.workspaces OWNER TO mlflow;

--
-- Name: experiments experiment_id; Type: DEFAULT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.experiments ALTER COLUMN experiment_id SET DEFAULT nextval('public.experiments_experiment_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.alembic_version (version_num) FROM stdin;
c3d6457b6d8a
\.


--
-- Data for Name: assessments; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.assessments (assessment_id, trace_id, name, assessment_type, value, error, created_timestamp, last_updated_timestamp, source_type, source_id, run_id, span_id, rationale, overrides, valid, assessment_metadata) FROM stdin;
\.


--
-- Data for Name: budget_policies; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.budget_policies (budget_policy_id, budget_unit, budget_amount, duration_unit, duration_value, target_scope, budget_action, created_by, created_at, last_updated_by, last_updated_at, workspace) FROM stdin;
\.


--
-- Data for Name: datasets; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.datasets (dataset_uuid, experiment_id, name, digest, dataset_source_type, dataset_source, dataset_schema, dataset_profile) FROM stdin;
409e959db22641df8f77f2901afd3976	1	imdb-test	071e32ee	local	{"uri": "data/raw/aclImdb"}	{"mlflow_colspec": [{"type": "string", "name": "text", "required": true}, {"type": "long", "name": "label", "required": true}]}	{"num_rows": 100, "num_elements": 200}
82e1b62cca2f4beea4fef2842147b0c2	1	imdb-test	f49bb785	local	{"uri": "data/raw/aclImdb"}	{"mlflow_colspec": [{"type": "string", "name": "text", "required": true}, {"type": "long", "name": "label", "required": true}]}	{"num_rows": 500, "num_elements": 1000}
a518e9d2248546db80f5da0a481a4770	1	imdb-test	888a2874	local	{"uri": "data/raw/aclImdb"}	{"mlflow_colspec": [{"type": "string", "name": "text", "required": true}, {"type": "long", "name": "label", "required": true}]}	{"num_rows": 250, "num_elements": 500}
f68d24d0d7de434fbd0136d265796630	1	imdb-test	1d362985	local	{"uri": "data/raw/aclImdb"}	{"mlflow_colspec": [{"type": "string", "name": "text", "required": true}, {"type": "long", "name": "label", "required": true}]}	{"num_rows": 1000, "num_elements": 2000}
b8fbf1d1065541cd841e799f7c0309f5	1	imdb-test	0e1dded1	local	{"uri": "data/raw/aclImdb"}	{"mlflow_colspec": [{"type": "string", "name": "text", "required": true}, {"type": "long", "name": "label", "required": true}]}	{"num_rows": 500, "num_elements": 1000}
5495b661b094453cab30f748987aaafc	1	imdb-test	9e14af77	local	{"uri": "data/raw/aclImdb"}	{"mlflow_colspec": [{"type": "string", "name": "text", "required": true}, {"type": "long", "name": "label", "required": true}]}	{"num_rows": 500, "num_elements": 1000}
\.


--
-- Data for Name: endpoint_bindings; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.endpoint_bindings (endpoint_id, resource_type, resource_id, created_at, created_by, last_updated_at, last_updated_by, display_name) FROM stdin;
\.


--
-- Data for Name: endpoint_model_mappings; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.endpoint_model_mappings (mapping_id, endpoint_id, model_definition_id, weight, created_by, created_at, linkage_type, fallback_order) FROM stdin;
\.


--
-- Data for Name: endpoint_tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.endpoint_tags (key, value, endpoint_id) FROM stdin;
\.


--
-- Data for Name: endpoints; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.endpoints (endpoint_id, name, created_by, created_at, last_updated_by, last_updated_at, routing_strategy, fallback_config_json, experiment_id, usage_tracking, workspace) FROM stdin;
\.


--
-- Data for Name: entity_associations; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.entity_associations (association_id, source_type, source_id, destination_type, destination_id, created_time) FROM stdin;
\.


--
-- Data for Name: evaluation_dataset_records; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.evaluation_dataset_records (dataset_record_id, dataset_id, inputs, expectations, tags, source, source_id, source_type, created_time, last_update_time, created_by, last_updated_by, input_hash, outputs) FROM stdin;
\.


--
-- Data for Name: evaluation_dataset_tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.evaluation_dataset_tags (dataset_id, key, value) FROM stdin;
\.


--
-- Data for Name: evaluation_datasets; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.evaluation_datasets (dataset_id, name, schema, profile, digest, created_time, last_update_time, created_by, last_updated_by, workspace) FROM stdin;
\.


--
-- Data for Name: experiment_tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.experiment_tags (key, value, experiment_id) FROM stdin;
\.


--
-- Data for Name: experiments; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.experiments (experiment_id, name, artifact_location, lifecycle_stage, creation_time, last_update_time, workspace) FROM stdin;
0	Default	mlflow-artifacts:/0	active	1776280487588	1776280487588	default
1	sentiment-imdb	mlflow-artifacts:/1	active	1776280513756	1776280513756	default
\.


--
-- Data for Name: input_tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.input_tags (input_uuid, name, value) FROM stdin;
3b203417014e4fcfb43dbca4a41cbef8	mlflow.data.context	evaluation
fd66d79e63b746409ff4352a295e160d	mlflow.data.context	evaluation
941a67bc4007490eab1e823bb022a91e	mlflow.data.context	evaluation
f9fdca911d7a49688547491975b3456b	mlflow.data.context	evaluation
c7bb88e57437469999c08127fc23c6ba	mlflow.data.context	evaluation
14d5dcab9d294e91bb9ffaba1ffd1f01	mlflow.data.context	evaluation
bbb9f19c6d2a41e19812c87b0eea7769	mlflow.data.context	evaluation
354f2f9e5f0c4296aa1bf1d368cfed17	mlflow.data.context	evaluation
f5fd2e23d32948509b42c446171e157c	mlflow.data.context	evaluation
e4e52f4c48cb4e06a26220c6ed25fbb0	mlflow.data.context	evaluation
\.


--
-- Data for Name: inputs; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.inputs (input_uuid, source_type, source_id, destination_type, destination_id, step) FROM stdin;
3b203417014e4fcfb43dbca4a41cbef8	DATASET	409e959db22641df8f77f2901afd3976	RUN	4ecd6e0653f54beaa2aa403283186710	0
fd66d79e63b746409ff4352a295e160d	DATASET	82e1b62cca2f4beea4fef2842147b0c2	RUN	1abce95a0c6d4d178b12f4d379f46d9c	0
941a67bc4007490eab1e823bb022a91e	DATASET	82e1b62cca2f4beea4fef2842147b0c2	RUN	d52e6c5075f848f68b4d252565d0556f	0
f9fdca911d7a49688547491975b3456b	DATASET	a518e9d2248546db80f5da0a481a4770	RUN	cd9898768eeb4c45a583d32cfa793374	0
c7bb88e57437469999c08127fc23c6ba	DATASET	82e1b62cca2f4beea4fef2842147b0c2	RUN	da82a11111e549e98434bc7bbe0669ee	0
14d5dcab9d294e91bb9ffaba1ffd1f01	DATASET	82e1b62cca2f4beea4fef2842147b0c2	RUN	978203d203794cd78bfaa52432f0661e	0
bbb9f19c6d2a41e19812c87b0eea7769	DATASET	82e1b62cca2f4beea4fef2842147b0c2	RUN	bfd2c72f1faf4b18a158aaf2207b4cd3	0
354f2f9e5f0c4296aa1bf1d368cfed17	DATASET	f68d24d0d7de434fbd0136d265796630	RUN	3bf05a9db5454052953cf40d7525b239	0
8f3fc93fa87b401b821a733ff5ef22ed	RUN_OUTPUT	3bf05a9db5454052953cf40d7525b239	MODEL_OUTPUT	m-9a3f7c164b03419299027ddcf63a2a31	0
f5fd2e23d32948509b42c446171e157c	DATASET	b8fbf1d1065541cd841e799f7c0309f5	RUN	5220471ebff74d7f9d261e8e1fe9af1a	0
e4e52f4c48cb4e06a26220c6ed25fbb0	DATASET	5495b661b094453cab30f748987aaafc	RUN	25e5cd8d08da4de498e1955cfa3be9bc	0
\.


--
-- Data for Name: issues; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.issues (issue_id, experiment_id, name, description, status, severity, root_causes, source_run_id, categories, created_timestamp, last_updated_timestamp, created_by) FROM stdin;
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.jobs (id, creation_time, job_name, params, timeout, status, result, retry_count, last_update_time, workspace, status_details) FROM stdin;
\.


--
-- Data for Name: latest_metrics; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.latest_metrics (key, value, "timestamp", step, is_nan, run_uuid) FROM stdin;
accuracy	0.89	1776280549096	0	f	4ecd6e0653f54beaa2aa403283186710
precision	0.8541666666666666	1776280549096	0	f	4ecd6e0653f54beaa2aa403283186710
recall	0.9111111111111111	1776280549096	0	f	4ecd6e0653f54beaa2aa403283186710
f1	0.8817204301075269	1776280549096	0	f	4ecd6e0653f54beaa2aa403283186710
accuracy	0.854	1776280946236	0	f	1abce95a0c6d4d178b12f4d379f46d9c
precision	0.8540772532188842	1776280946236	0	f	1abce95a0c6d4d178b12f4d379f46d9c
recall	0.8361344537815126	1776280946236	0	f	1abce95a0c6d4d178b12f4d379f46d9c
f1	0.8450106157112527	1776280946236	0	f	1abce95a0c6d4d178b12f4d379f46d9c
accuracy	0.886	1776281088826	0	f	d52e6c5075f848f68b4d252565d0556f
precision	0.905829596412556	1776281088826	0	f	d52e6c5075f848f68b4d252565d0556f
recall	0.8487394957983193	1776281088826	0	f	d52e6c5075f848f68b4d252565d0556f
f1	0.8763557483731019	1776281088826	0	f	d52e6c5075f848f68b4d252565d0556f
accuracy	0.904	1776281251951	0	f	cd9898768eeb4c45a583d32cfa793374
precision	0.9203539823008849	1776281251951	0	f	cd9898768eeb4c45a583d32cfa793374
recall	0.8739495798319328	1776281251951	0	f	cd9898768eeb4c45a583d32cfa793374
f1	0.896551724137931	1776281251951	0	f	cd9898768eeb4c45a583d32cfa793374
accuracy	0.914	1776281474954	0	f	da82a11111e549e98434bc7bbe0669ee
precision	0.922077922077922	1776281474954	0	f	da82a11111e549e98434bc7bbe0669ee
recall	0.8949579831932774	1776281474954	0	f	da82a11111e549e98434bc7bbe0669ee
f1	0.908315565031983	1776281474954	0	f	da82a11111e549e98434bc7bbe0669ee
accuracy	0.914	1776281664561	0	f	978203d203794cd78bfaa52432f0661e
precision	0.922077922077922	1776281664561	0	f	978203d203794cd78bfaa52432f0661e
recall	0.8949579831932774	1776281664561	0	f	978203d203794cd78bfaa52432f0661e
f1	0.908315565031983	1776281664561	0	f	978203d203794cd78bfaa52432f0661e
accuracy	0.914	1776281919231	0	f	bfd2c72f1faf4b18a158aaf2207b4cd3
precision	0.922077922077922	1776281919231	0	f	bfd2c72f1faf4b18a158aaf2207b4cd3
recall	0.8949579831932774	1776281919231	0	f	bfd2c72f1faf4b18a158aaf2207b4cd3
f1	0.908315565031983	1776281919231	0	f	bfd2c72f1faf4b18a158aaf2207b4cd3
accuracy	0.9	1776282301008	0	f	3bf05a9db5454052953cf40d7525b239
precision	0.9311827956989247	1776282301008	0	f	3bf05a9db5454052953cf40d7525b239
recall	0.8642714570858283	1776282301008	0	f	3bf05a9db5454052953cf40d7525b239
f1	0.8964803312629399	1776282301008	0	f	3bf05a9db5454052953cf40d7525b239
accuracy	0.908	1776285046825	0	f	5220471ebff74d7f9d261e8e1fe9af1a
precision	0.9205020920502092	1776285046825	0	f	5220471ebff74d7f9d261e8e1fe9af1a
recall	0.8906882591093117	1776285046825	0	f	5220471ebff74d7f9d261e8e1fe9af1a
f1	0.9053497942386831	1776285046825	0	f	5220471ebff74d7f9d261e8e1fe9af1a
accuracy	0.904	1776285253084	0	f	25e5cd8d08da4de498e1955cfa3be9bc
precision	0.9246861924686193	1776285253084	0	f	25e5cd8d08da4de498e1955cfa3be9bc
recall	0.8804780876494024	1776285253084	0	f	25e5cd8d08da4de498e1955cfa3be9bc
f1	0.9020408163265307	1776285253084	0	f	25e5cd8d08da4de498e1955cfa3be9bc
\.


--
-- Data for Name: logged_model_metrics; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.logged_model_metrics (model_id, metric_name, metric_timestamp_ms, metric_step, metric_value, experiment_id, run_id, dataset_uuid, dataset_name, dataset_digest) FROM stdin;
m-9a3f7c164b03419299027ddcf63a2a31	accuracy	1776282301008	0	0.9	1	3bf05a9db5454052953cf40d7525b239	\N	\N	\N
m-9a3f7c164b03419299027ddcf63a2a31	precision	1776282301008	0	0.9311827956989247	1	3bf05a9db5454052953cf40d7525b239	\N	\N	\N
m-9a3f7c164b03419299027ddcf63a2a31	recall	1776282301008	0	0.8642714570858283	1	3bf05a9db5454052953cf40d7525b239	\N	\N	\N
m-9a3f7c164b03419299027ddcf63a2a31	f1	1776282301008	0	0.8964803312629399	1	3bf05a9db5454052953cf40d7525b239	\N	\N	\N
\.


--
-- Data for Name: logged_model_params; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.logged_model_params (model_id, experiment_id, param_key, param_value) FROM stdin;
m-9a3f7c164b03419299027ddcf63a2a31	1	data_dir	data/raw/aclImdb
m-9a3f7c164b03419299027ddcf63a2a31	1	split	test
m-9a3f7c164b03419299027ddcf63a2a31	1	sample_size	1000
m-9a3f7c164b03419299027ddcf63a2a31	1	batch_size	8
m-9a3f7c164b03419299027ddcf63a2a31	1	max_length	512
m-9a3f7c164b03419299027ddcf63a2a31	1	random_seed	42
m-9a3f7c164b03419299027ddcf63a2a31	1	model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english
m-9a3f7c164b03419299027ddcf63a2a31	1	preprocess_version	v1
\.


--
-- Data for Name: logged_model_tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.logged_model_tags (model_id, experiment_id, tag_key, tag_value) FROM stdin;
m-9a3f7c164b03419299027ddcf63a2a31	1	mlflow.user	lucasmartins
m-9a3f7c164b03419299027ddcf63a2a31	1	mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py
m-9a3f7c164b03419299027ddcf63a2a31	1	mlflow.source.type	LOCAL
m-9a3f7c164b03419299027ddcf63a2a31	1	mlflow.source.git.commit	8a59a5298721844f67051be0748d50563b5019bf
m-9a3f7c164b03419299027ddcf63a2a31	1	mlflow.modelVersions	[{"name": "sentiment-imdb", "version": 1}, {"name": "sentiment-imdb", "version": "1"}]
\.


--
-- Data for Name: logged_models; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.logged_models (model_id, experiment_id, name, artifact_location, creation_timestamp_ms, last_updated_timestamp_ms, status, lifecycle_stage, model_type, source_run_id, status_message) FROM stdin;
m-9a3f7c164b03419299027ddcf63a2a31	1	model	mlflow-artifacts:/1/models/m-9a3f7c164b03419299027ddcf63a2a31/artifacts	1776282301228	1776282404649	2	active		3bf05a9db5454052953cf40d7525b239	\N
\.


--
-- Data for Name: metrics; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.metrics (key, value, "timestamp", run_uuid, step, is_nan) FROM stdin;
accuracy	0.89	1776280549096	4ecd6e0653f54beaa2aa403283186710	0	f
precision	0.8541666666666666	1776280549096	4ecd6e0653f54beaa2aa403283186710	0	f
recall	0.9111111111111111	1776280549096	4ecd6e0653f54beaa2aa403283186710	0	f
f1	0.8817204301075269	1776280549096	4ecd6e0653f54beaa2aa403283186710	0	f
accuracy	0.854	1776280946236	1abce95a0c6d4d178b12f4d379f46d9c	0	f
precision	0.8540772532188842	1776280946236	1abce95a0c6d4d178b12f4d379f46d9c	0	f
recall	0.8361344537815126	1776280946236	1abce95a0c6d4d178b12f4d379f46d9c	0	f
f1	0.8450106157112527	1776280946236	1abce95a0c6d4d178b12f4d379f46d9c	0	f
accuracy	0.886	1776281088826	d52e6c5075f848f68b4d252565d0556f	0	f
precision	0.905829596412556	1776281088826	d52e6c5075f848f68b4d252565d0556f	0	f
recall	0.8487394957983193	1776281088826	d52e6c5075f848f68b4d252565d0556f	0	f
f1	0.8763557483731019	1776281088826	d52e6c5075f848f68b4d252565d0556f	0	f
accuracy	0.904	1776281251951	cd9898768eeb4c45a583d32cfa793374	0	f
precision	0.9203539823008849	1776281251951	cd9898768eeb4c45a583d32cfa793374	0	f
recall	0.8739495798319328	1776281251951	cd9898768eeb4c45a583d32cfa793374	0	f
f1	0.896551724137931	1776281251951	cd9898768eeb4c45a583d32cfa793374	0	f
accuracy	0.914	1776281474954	da82a11111e549e98434bc7bbe0669ee	0	f
precision	0.922077922077922	1776281474954	da82a11111e549e98434bc7bbe0669ee	0	f
recall	0.8949579831932774	1776281474954	da82a11111e549e98434bc7bbe0669ee	0	f
f1	0.908315565031983	1776281474954	da82a11111e549e98434bc7bbe0669ee	0	f
accuracy	0.914	1776281664561	978203d203794cd78bfaa52432f0661e	0	f
precision	0.922077922077922	1776281664561	978203d203794cd78bfaa52432f0661e	0	f
recall	0.8949579831932774	1776281664561	978203d203794cd78bfaa52432f0661e	0	f
f1	0.908315565031983	1776281664561	978203d203794cd78bfaa52432f0661e	0	f
accuracy	0.914	1776281919231	bfd2c72f1faf4b18a158aaf2207b4cd3	0	f
precision	0.922077922077922	1776281919231	bfd2c72f1faf4b18a158aaf2207b4cd3	0	f
recall	0.8949579831932774	1776281919231	bfd2c72f1faf4b18a158aaf2207b4cd3	0	f
f1	0.908315565031983	1776281919231	bfd2c72f1faf4b18a158aaf2207b4cd3	0	f
accuracy	0.9	1776282301008	3bf05a9db5454052953cf40d7525b239	0	f
precision	0.9311827956989247	1776282301008	3bf05a9db5454052953cf40d7525b239	0	f
recall	0.8642714570858283	1776282301008	3bf05a9db5454052953cf40d7525b239	0	f
f1	0.8964803312629399	1776282301008	3bf05a9db5454052953cf40d7525b239	0	f
accuracy	0.908	1776285046825	5220471ebff74d7f9d261e8e1fe9af1a	0	f
precision	0.9205020920502092	1776285046825	5220471ebff74d7f9d261e8e1fe9af1a	0	f
recall	0.8906882591093117	1776285046825	5220471ebff74d7f9d261e8e1fe9af1a	0	f
f1	0.9053497942386831	1776285046825	5220471ebff74d7f9d261e8e1fe9af1a	0	f
accuracy	0.904	1776285253084	25e5cd8d08da4de498e1955cfa3be9bc	0	f
precision	0.9246861924686193	1776285253084	25e5cd8d08da4de498e1955cfa3be9bc	0	f
recall	0.8804780876494024	1776285253084	25e5cd8d08da4de498e1955cfa3be9bc	0	f
f1	0.9020408163265307	1776285253084	25e5cd8d08da4de498e1955cfa3be9bc	0	f
\.


--
-- Data for Name: model_definitions; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.model_definitions (model_definition_id, name, secret_id, provider, model_name, created_by, created_at, last_updated_by, last_updated_at, workspace) FROM stdin;
\.


--
-- Data for Name: model_version_tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.model_version_tags (key, value, name, version, workspace) FROM stdin;
\.


--
-- Data for Name: model_versions; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.model_versions (name, version, creation_time, last_updated_time, description, user_id, current_stage, source, run_id, status, status_message, run_link, storage_location, workspace) FROM stdin;
sentiment-imdb	1	1776282406127	1776282406127		\N	None	models:/m-9a3f7c164b03419299027ddcf63a2a31	3bf05a9db5454052953cf40d7525b239	READY	\N		mlflow-artifacts:/1/models/m-9a3f7c164b03419299027ddcf63a2a31/artifacts	default
\.


--
-- Data for Name: online_scoring_configs; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.online_scoring_configs (online_scoring_config_id, scorer_id, sample_rate, experiment_id, filter_string) FROM stdin;
\.


--
-- Data for Name: params; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.params (key, value, run_uuid) FROM stdin;
data_dir	data/raw/aclImdb	4ecd6e0653f54beaa2aa403283186710
split	test	4ecd6e0653f54beaa2aa403283186710
sample_size	100	4ecd6e0653f54beaa2aa403283186710
batch_size	8	4ecd6e0653f54beaa2aa403283186710
max_length	512	4ecd6e0653f54beaa2aa403283186710
random_seed	42	4ecd6e0653f54beaa2aa403283186710
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	4ecd6e0653f54beaa2aa403283186710
preprocess_version	v1	4ecd6e0653f54beaa2aa403283186710
data_dir	data/raw/aclImdb	1abce95a0c6d4d178b12f4d379f46d9c
split	test	1abce95a0c6d4d178b12f4d379f46d9c
sample_size	500	1abce95a0c6d4d178b12f4d379f46d9c
batch_size	8	1abce95a0c6d4d178b12f4d379f46d9c
max_length	128	1abce95a0c6d4d178b12f4d379f46d9c
random_seed	42	1abce95a0c6d4d178b12f4d379f46d9c
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	1abce95a0c6d4d178b12f4d379f46d9c
preprocess_version	v1	1abce95a0c6d4d178b12f4d379f46d9c
data_dir	data/raw/aclImdb	d52e6c5075f848f68b4d252565d0556f
split	test	d52e6c5075f848f68b4d252565d0556f
sample_size	500	d52e6c5075f848f68b4d252565d0556f
batch_size	8	d52e6c5075f848f68b4d252565d0556f
max_length	256	d52e6c5075f848f68b4d252565d0556f
random_seed	42	d52e6c5075f848f68b4d252565d0556f
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	d52e6c5075f848f68b4d252565d0556f
preprocess_version	v1	d52e6c5075f848f68b4d252565d0556f
data_dir	data/raw/aclImdb	cd9898768eeb4c45a583d32cfa793374
split	test	cd9898768eeb4c45a583d32cfa793374
sample_size	250	cd9898768eeb4c45a583d32cfa793374
batch_size	8	cd9898768eeb4c45a583d32cfa793374
max_length	512	cd9898768eeb4c45a583d32cfa793374
random_seed	42	cd9898768eeb4c45a583d32cfa793374
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	cd9898768eeb4c45a583d32cfa793374
preprocess_version	v1	cd9898768eeb4c45a583d32cfa793374
data_dir	data/raw/aclImdb	da82a11111e549e98434bc7bbe0669ee
split	test	da82a11111e549e98434bc7bbe0669ee
sample_size	500	da82a11111e549e98434bc7bbe0669ee
batch_size	8	da82a11111e549e98434bc7bbe0669ee
max_length	512	da82a11111e549e98434bc7bbe0669ee
random_seed	43	da82a11111e549e98434bc7bbe0669ee
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	da82a11111e549e98434bc7bbe0669ee
preprocess_version	v1	da82a11111e549e98434bc7bbe0669ee
data_dir	data/raw/aclImdb	978203d203794cd78bfaa52432f0661e
split	test	978203d203794cd78bfaa52432f0661e
sample_size	500	978203d203794cd78bfaa52432f0661e
batch_size	8	978203d203794cd78bfaa52432f0661e
max_length	512	978203d203794cd78bfaa52432f0661e
random_seed	44	978203d203794cd78bfaa52432f0661e
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	978203d203794cd78bfaa52432f0661e
preprocess_version	v1	978203d203794cd78bfaa52432f0661e
data_dir	data/raw/aclImdb	bfd2c72f1faf4b18a158aaf2207b4cd3
split	test	bfd2c72f1faf4b18a158aaf2207b4cd3
sample_size	500	bfd2c72f1faf4b18a158aaf2207b4cd3
batch_size	8	bfd2c72f1faf4b18a158aaf2207b4cd3
max_length	512	bfd2c72f1faf4b18a158aaf2207b4cd3
random_seed	42	bfd2c72f1faf4b18a158aaf2207b4cd3
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	bfd2c72f1faf4b18a158aaf2207b4cd3
preprocess_version	v1	bfd2c72f1faf4b18a158aaf2207b4cd3
data_dir	data/raw/aclImdb	3bf05a9db5454052953cf40d7525b239
split	test	3bf05a9db5454052953cf40d7525b239
sample_size	1000	3bf05a9db5454052953cf40d7525b239
batch_size	8	3bf05a9db5454052953cf40d7525b239
max_length	512	3bf05a9db5454052953cf40d7525b239
random_seed	42	3bf05a9db5454052953cf40d7525b239
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	3bf05a9db5454052953cf40d7525b239
preprocess_version	v1	3bf05a9db5454052953cf40d7525b239
data_dir	data/raw/aclImdb	5220471ebff74d7f9d261e8e1fe9af1a
split	test	5220471ebff74d7f9d261e8e1fe9af1a
sample_size	500	5220471ebff74d7f9d261e8e1fe9af1a
batch_size	8	5220471ebff74d7f9d261e8e1fe9af1a
max_length	512	5220471ebff74d7f9d261e8e1fe9af1a
random_seed	43	5220471ebff74d7f9d261e8e1fe9af1a
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	5220471ebff74d7f9d261e8e1fe9af1a
preprocess_version	v1	5220471ebff74d7f9d261e8e1fe9af1a
data_dir	data/raw/aclImdb	25e5cd8d08da4de498e1955cfa3be9bc
split	test	25e5cd8d08da4de498e1955cfa3be9bc
sample_size	500	25e5cd8d08da4de498e1955cfa3be9bc
batch_size	8	25e5cd8d08da4de498e1955cfa3be9bc
max_length	512	25e5cd8d08da4de498e1955cfa3be9bc
random_seed	44	25e5cd8d08da4de498e1955cfa3be9bc
model_name	distilbert/distilbert-base-uncased-finetuned-sst-2-english	25e5cd8d08da4de498e1955cfa3be9bc
preprocess_version	v1	25e5cd8d08da4de498e1955cfa3be9bc
\.


--
-- Data for Name: registered_model_aliases; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.registered_model_aliases (alias, version, name, workspace) FROM stdin;
\.


--
-- Data for Name: registered_model_tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.registered_model_tags (key, value, name, workspace) FROM stdin;
\.


--
-- Data for Name: registered_models; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.registered_models (name, creation_time, last_updated_time, description, workspace) FROM stdin;
sentiment-imdb	1776282405988	1776282406127		default
\.


--
-- Data for Name: runs; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.runs (run_uuid, name, source_type, source_name, entry_point_name, user_id, status, start_time, end_time, source_version, lifecycle_stage, artifact_uri, experiment_id, deleted_time) FROM stdin;
4ecd6e0653f54beaa2aa403283186710	size-100	UNKNOWN			lucasmartins	FINISHED	1776280513838	1776280549274		active	mlflow-artifacts:/1/4ecd6e0653f54beaa2aa403283186710/artifacts	1	\N
1abce95a0c6d4d178b12f4d379f46d9c	maxlen-128	UNKNOWN			lucasmartins	FINISHED	1776280906360	1776280946428		active	mlflow-artifacts:/1/1abce95a0c6d4d178b12f4d379f46d9c/artifacts	1	\N
d52e6c5075f848f68b4d252565d0556f	maxlen-256	UNKNOWN			lucasmartins	FINISHED	1776281007333	1776281089006		active	mlflow-artifacts:/1/d52e6c5075f848f68b4d252565d0556f/artifacts	1	\N
cd9898768eeb4c45a583d32cfa793374	size-250	UNKNOWN			lucasmartins	FINISHED	1776281169123	1776281252092		active	mlflow-artifacts:/1/cd9898768eeb4c45a583d32cfa793374/artifacts	1	\N
bfd2c72f1faf4b18a158aaf2207b4cd3	size-500	UNKNOWN			lucasmartins	FINISHED	1776281743457	1776281919370		active	mlflow-artifacts:/1/bfd2c72f1faf4b18a158aaf2207b4cd3/artifacts	1	\N
3bf05a9db5454052953cf40d7525b239	baseline-1000	UNKNOWN			lucasmartins	FINISHED	1776281953053	1776282406264		active	mlflow-artifacts:/1/3bf05a9db5454052953cf40d7525b239/artifacts	1	\N
978203d203794cd78bfaa52432f0661e	seed-44	UNKNOWN			lucasmartins	FINISHED	1776281497429	1776281664751		deleted	mlflow-artifacts:/1/978203d203794cd78bfaa52432f0661e/artifacts	1	1776284822858
da82a11111e549e98434bc7bbe0669ee	seed-43	UNKNOWN			lucasmartins	FINISHED	1776281308870	1776281475116		deleted	mlflow-artifacts:/1/da82a11111e549e98434bc7bbe0669ee/artifacts	1	1776284822859
5220471ebff74d7f9d261e8e1fe9af1a	seed-43	UNKNOWN			lucasmartins	FINISHED	1776284865209	1776285047005		active	mlflow-artifacts:/1/5220471ebff74d7f9d261e8e1fe9af1a/artifacts	1	\N
25e5cd8d08da4de498e1955cfa3be9bc	seed-44	UNKNOWN			lucasmartins	FINISHED	1776285087139	1776285253295		active	mlflow-artifacts:/1/25e5cd8d08da4de498e1955cfa3be9bc/artifacts	1	\N
\.


--
-- Data for Name: scorer_versions; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.scorer_versions (scorer_id, scorer_version, serialized_scorer, creation_time) FROM stdin;
\.


--
-- Data for Name: scorers; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.scorers (experiment_id, scorer_name, scorer_id) FROM stdin;
\.


--
-- Data for Name: secrets; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.secrets (secret_id, secret_name, encrypted_value, wrapped_dek, kek_version, masked_value, provider, auth_config, description, created_by, created_at, last_updated_by, last_updated_at, workspace) FROM stdin;
\.


--
-- Data for Name: span_metrics; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.span_metrics (trace_id, span_id, key, value) FROM stdin;
\.


--
-- Data for Name: spans; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.spans (trace_id, experiment_id, span_id, parent_span_id, name, type, status, start_time_unix_nano, end_time_unix_nano, content, dimension_attributes) FROM stdin;
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.tags (key, value, run_uuid) FROM stdin;
mlflow.user	lucasmartins	4ecd6e0653f54beaa2aa403283186710
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	4ecd6e0653f54beaa2aa403283186710
mlflow.source.type	LOCAL	4ecd6e0653f54beaa2aa403283186710
mlflow.source.git.commit	9c76a24f53928f9b0eeb45560ee0bf4c69e503de	4ecd6e0653f54beaa2aa403283186710
mlflow.runName	size-100	4ecd6e0653f54beaa2aa403283186710
mlflow.user	lucasmartins	1abce95a0c6d4d178b12f4d379f46d9c
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	1abce95a0c6d4d178b12f4d379f46d9c
mlflow.source.type	LOCAL	1abce95a0c6d4d178b12f4d379f46d9c
mlflow.source.git.commit	f0326211ec9cc4ea7f856f3fa0a40bdae7b46797	1abce95a0c6d4d178b12f4d379f46d9c
mlflow.runName	maxlen-128	1abce95a0c6d4d178b12f4d379f46d9c
mlflow.user	lucasmartins	d52e6c5075f848f68b4d252565d0556f
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	d52e6c5075f848f68b4d252565d0556f
mlflow.source.type	LOCAL	d52e6c5075f848f68b4d252565d0556f
mlflow.source.git.commit	fee72d8183579f0144c302adff3b84d35ec90609	d52e6c5075f848f68b4d252565d0556f
mlflow.runName	maxlen-256	d52e6c5075f848f68b4d252565d0556f
mlflow.user	lucasmartins	cd9898768eeb4c45a583d32cfa793374
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	cd9898768eeb4c45a583d32cfa793374
mlflow.source.type	LOCAL	cd9898768eeb4c45a583d32cfa793374
mlflow.source.git.commit	65f1e5fbefd1f755c2e51c1e2e9e002a581accc0	cd9898768eeb4c45a583d32cfa793374
mlflow.runName	size-250	cd9898768eeb4c45a583d32cfa793374
mlflow.user	lucasmartins	da82a11111e549e98434bc7bbe0669ee
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	da82a11111e549e98434bc7bbe0669ee
mlflow.source.type	LOCAL	da82a11111e549e98434bc7bbe0669ee
mlflow.source.git.commit	4174cf1043dd2e4617913e7577daa29600542069	da82a11111e549e98434bc7bbe0669ee
mlflow.runName	seed-43	da82a11111e549e98434bc7bbe0669ee
mlflow.user	lucasmartins	978203d203794cd78bfaa52432f0661e
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	978203d203794cd78bfaa52432f0661e
mlflow.source.type	LOCAL	978203d203794cd78bfaa52432f0661e
mlflow.source.git.commit	a7c52b73637393a0bac47f2ee59bc72abea1b069	978203d203794cd78bfaa52432f0661e
mlflow.runName	seed-44	978203d203794cd78bfaa52432f0661e
mlflow.user	lucasmartins	bfd2c72f1faf4b18a158aaf2207b4cd3
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	bfd2c72f1faf4b18a158aaf2207b4cd3
mlflow.source.type	LOCAL	bfd2c72f1faf4b18a158aaf2207b4cd3
mlflow.source.git.commit	230191a36083bd73bfd40dadddba4ba8e84b43b8	bfd2c72f1faf4b18a158aaf2207b4cd3
mlflow.runName	size-500	bfd2c72f1faf4b18a158aaf2207b4cd3
mlflow.user	lucasmartins	3bf05a9db5454052953cf40d7525b239
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	3bf05a9db5454052953cf40d7525b239
mlflow.source.type	LOCAL	3bf05a9db5454052953cf40d7525b239
mlflow.source.git.commit	8a59a5298721844f67051be0748d50563b5019bf	3bf05a9db5454052953cf40d7525b239
mlflow.runName	baseline-1000	3bf05a9db5454052953cf40d7525b239
mlflow.user	lucasmartins	5220471ebff74d7f9d261e8e1fe9af1a
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	5220471ebff74d7f9d261e8e1fe9af1a
mlflow.source.type	LOCAL	5220471ebff74d7f9d261e8e1fe9af1a
mlflow.source.git.commit	21c13b3f3273504f45f8dd7415ffa3241711b8c5	5220471ebff74d7f9d261e8e1fe9af1a
mlflow.runName	seed-43	5220471ebff74d7f9d261e8e1fe9af1a
mlflow.user	lucasmartins	25e5cd8d08da4de498e1955cfa3be9bc
mlflow.source.name	/home/lucasmartins/sml/Projetos-Individuais-2026-1/projeto-individual-2/sentimental-analysis-on-movie-reviews/src/pipeline.py	25e5cd8d08da4de498e1955cfa3be9bc
mlflow.source.type	LOCAL	25e5cd8d08da4de498e1955cfa3be9bc
mlflow.source.git.commit	21c13b3f3273504f45f8dd7415ffa3241711b8c5	25e5cd8d08da4de498e1955cfa3be9bc
mlflow.runName	seed-44	25e5cd8d08da4de498e1955cfa3be9bc
\.


--
-- Data for Name: trace_info; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.trace_info (request_id, experiment_id, timestamp_ms, execution_time_ms, status, client_request_id, request_preview, response_preview) FROM stdin;
\.


--
-- Data for Name: trace_metrics; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.trace_metrics (request_id, key, value) FROM stdin;
\.


--
-- Data for Name: trace_request_metadata; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.trace_request_metadata (key, value, request_id) FROM stdin;
\.


--
-- Data for Name: trace_tags; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.trace_tags (key, value, request_id) FROM stdin;
\.


--
-- Data for Name: webhook_events; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.webhook_events (webhook_id, entity, action) FROM stdin;
\.


--
-- Data for Name: webhooks; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.webhooks (webhook_id, name, description, url, status, secret, creation_timestamp, last_updated_timestamp, deleted_timestamp, workspace) FROM stdin;
\.


--
-- Data for Name: workspaces; Type: TABLE DATA; Schema: public; Owner: mlflow
--

COPY public.workspaces (name, description, default_artifact_root) FROM stdin;
default	Default workspace for legacy resources	\N
\.


--
-- Name: experiments_experiment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mlflow
--

SELECT pg_catalog.setval('public.experiments_experiment_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: assessments assessments_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT assessments_pk PRIMARY KEY (assessment_id);


--
-- Name: budget_policies budget_policies_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.budget_policies
    ADD CONSTRAINT budget_policies_pk PRIMARY KEY (budget_policy_id);


--
-- Name: datasets dataset_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT dataset_pk PRIMARY KEY (experiment_id, name, digest);


--
-- Name: endpoint_bindings endpoint_bindings_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoint_bindings
    ADD CONSTRAINT endpoint_bindings_pk PRIMARY KEY (endpoint_id, resource_type, resource_id);


--
-- Name: endpoint_model_mappings endpoint_model_mappings_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoint_model_mappings
    ADD CONSTRAINT endpoint_model_mappings_pk PRIMARY KEY (mapping_id);


--
-- Name: endpoint_tags endpoint_tag_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoint_tags
    ADD CONSTRAINT endpoint_tag_pk PRIMARY KEY (key, endpoint_id);


--
-- Name: endpoints endpoints_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoints
    ADD CONSTRAINT endpoints_pk PRIMARY KEY (endpoint_id);


--
-- Name: entity_associations entity_associations_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.entity_associations
    ADD CONSTRAINT entity_associations_pk PRIMARY KEY (source_type, source_id, destination_type, destination_id);


--
-- Name: evaluation_dataset_records evaluation_dataset_records_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.evaluation_dataset_records
    ADD CONSTRAINT evaluation_dataset_records_pk PRIMARY KEY (dataset_record_id);


--
-- Name: evaluation_dataset_tags evaluation_dataset_tags_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.evaluation_dataset_tags
    ADD CONSTRAINT evaluation_dataset_tags_pk PRIMARY KEY (dataset_id, key);


--
-- Name: evaluation_datasets evaluation_datasets_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.evaluation_datasets
    ADD CONSTRAINT evaluation_datasets_pk PRIMARY KEY (dataset_id);


--
-- Name: experiments experiment_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiment_pk PRIMARY KEY (experiment_id);


--
-- Name: experiment_tags experiment_tag_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.experiment_tags
    ADD CONSTRAINT experiment_tag_pk PRIMARY KEY (key, experiment_id);


--
-- Name: input_tags input_tags_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.input_tags
    ADD CONSTRAINT input_tags_pk PRIMARY KEY (input_uuid, name);


--
-- Name: inputs inputs_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.inputs
    ADD CONSTRAINT inputs_pk PRIMARY KEY (source_type, source_id, destination_type, destination_id);


--
-- Name: issues issues_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT issues_pk PRIMARY KEY (issue_id);


--
-- Name: jobs jobs_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pk PRIMARY KEY (id);


--
-- Name: latest_metrics latest_metric_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.latest_metrics
    ADD CONSTRAINT latest_metric_pk PRIMARY KEY (key, run_uuid);


--
-- Name: logged_model_metrics logged_model_metrics_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_metrics
    ADD CONSTRAINT logged_model_metrics_pk PRIMARY KEY (model_id, metric_name, metric_timestamp_ms, metric_step, run_id);


--
-- Name: logged_model_params logged_model_params_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_params
    ADD CONSTRAINT logged_model_params_pk PRIMARY KEY (model_id, param_key);


--
-- Name: logged_model_tags logged_model_tags_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_tags
    ADD CONSTRAINT logged_model_tags_pk PRIMARY KEY (model_id, tag_key);


--
-- Name: logged_models logged_models_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_models
    ADD CONSTRAINT logged_models_pk PRIMARY KEY (model_id);


--
-- Name: metrics metric_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metric_pk PRIMARY KEY (key, "timestamp", step, run_uuid, value, is_nan);


--
-- Name: model_definitions model_definitions_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.model_definitions
    ADD CONSTRAINT model_definitions_pk PRIMARY KEY (model_definition_id);


--
-- Name: model_versions model_version_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_version_pk PRIMARY KEY (workspace, name, version);


--
-- Name: model_version_tags model_version_tag_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.model_version_tags
    ADD CONSTRAINT model_version_tag_pk PRIMARY KEY (workspace, key, name, version);


--
-- Name: online_scoring_configs online_scoring_config_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.online_scoring_configs
    ADD CONSTRAINT online_scoring_config_pk PRIMARY KEY (online_scoring_config_id);


--
-- Name: params param_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.params
    ADD CONSTRAINT param_pk PRIMARY KEY (key, run_uuid);


--
-- Name: registered_model_aliases registered_model_alias_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.registered_model_aliases
    ADD CONSTRAINT registered_model_alias_pk PRIMARY KEY (workspace, name, alias);


--
-- Name: registered_models registered_model_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.registered_models
    ADD CONSTRAINT registered_model_pk PRIMARY KEY (workspace, name);


--
-- Name: registered_model_tags registered_model_tag_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.registered_model_tags
    ADD CONSTRAINT registered_model_tag_pk PRIMARY KEY (workspace, key, name);


--
-- Name: runs run_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT run_pk PRIMARY KEY (run_uuid);


--
-- Name: scorers scorer_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.scorers
    ADD CONSTRAINT scorer_pk PRIMARY KEY (scorer_id);


--
-- Name: scorer_versions scorer_version_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.scorer_versions
    ADD CONSTRAINT scorer_version_pk PRIMARY KEY (scorer_id, scorer_version);


--
-- Name: secrets secrets_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.secrets
    ADD CONSTRAINT secrets_pk PRIMARY KEY (secret_id);


--
-- Name: span_metrics span_metrics_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.span_metrics
    ADD CONSTRAINT span_metrics_pk PRIMARY KEY (trace_id, span_id, key);


--
-- Name: spans spans_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.spans
    ADD CONSTRAINT spans_pk PRIMARY KEY (trace_id, span_id);


--
-- Name: tags tag_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tag_pk PRIMARY KEY (key, run_uuid);


--
-- Name: trace_info trace_info_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.trace_info
    ADD CONSTRAINT trace_info_pk PRIMARY KEY (request_id);


--
-- Name: trace_metrics trace_metrics_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.trace_metrics
    ADD CONSTRAINT trace_metrics_pk PRIMARY KEY (request_id, key);


--
-- Name: trace_request_metadata trace_request_metadata_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.trace_request_metadata
    ADD CONSTRAINT trace_request_metadata_pk PRIMARY KEY (key, request_id);


--
-- Name: trace_tags trace_tag_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.trace_tags
    ADD CONSTRAINT trace_tag_pk PRIMARY KEY (key, request_id);


--
-- Name: evaluation_dataset_records unique_dataset_input; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.evaluation_dataset_records
    ADD CONSTRAINT unique_dataset_input UNIQUE (dataset_id, input_hash);


--
-- Name: endpoints uq_endpoints_workspace_name; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoints
    ADD CONSTRAINT uq_endpoints_workspace_name UNIQUE (workspace, name);


--
-- Name: experiments uq_experiments_workspace_name; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT uq_experiments_workspace_name UNIQUE (workspace, name);


--
-- Name: model_definitions uq_model_definitions_workspace_name; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.model_definitions
    ADD CONSTRAINT uq_model_definitions_workspace_name UNIQUE (workspace, name);


--
-- Name: secrets uq_secrets_workspace_secret_name; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.secrets
    ADD CONSTRAINT uq_secrets_workspace_secret_name UNIQUE (workspace, secret_name);


--
-- Name: webhook_events webhook_event_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.webhook_events
    ADD CONSTRAINT webhook_event_pk PRIMARY KEY (webhook_id, entity, action);


--
-- Name: webhooks webhook_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.webhooks
    ADD CONSTRAINT webhook_pk PRIMARY KEY (webhook_id);


--
-- Name: workspaces workspaces_pk; Type: CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.workspaces
    ADD CONSTRAINT workspaces_pk PRIMARY KEY (name);


--
-- Name: idx_budget_policies_workspace; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_budget_policies_workspace ON public.budget_policies USING btree (workspace);


--
-- Name: idx_endpoints_workspace; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_endpoints_workspace ON public.endpoints USING btree (workspace);


--
-- Name: idx_evaluation_datasets_workspace; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_evaluation_datasets_workspace ON public.evaluation_datasets USING btree (workspace);


--
-- Name: idx_experiments_workspace; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_experiments_workspace ON public.experiments USING btree (workspace);


--
-- Name: idx_experiments_workspace_creation_time; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_experiments_workspace_creation_time ON public.experiments USING btree (workspace, creation_time);


--
-- Name: idx_model_definitions_workspace; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_model_definitions_workspace ON public.model_definitions USING btree (workspace);


--
-- Name: idx_registered_models_workspace; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_registered_models_workspace ON public.registered_models USING btree (workspace);


--
-- Name: idx_secrets_workspace; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_secrets_workspace ON public.secrets USING btree (workspace);


--
-- Name: idx_webhook_events_action; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_webhook_events_action ON public.webhook_events USING btree (action);


--
-- Name: idx_webhook_events_entity; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_webhook_events_entity ON public.webhook_events USING btree (entity);


--
-- Name: idx_webhook_events_entity_action; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_webhook_events_entity_action ON public.webhook_events USING btree (entity, action);


--
-- Name: idx_webhooks_name; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_webhooks_name ON public.webhooks USING btree (name);


--
-- Name: idx_webhooks_status; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_webhooks_status ON public.webhooks USING btree (status);


--
-- Name: idx_webhooks_workspace; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX idx_webhooks_workspace ON public.webhooks USING btree (workspace);


--
-- Name: index_assessments_assessment_type; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_assessments_assessment_type ON public.assessments USING btree (assessment_type);


--
-- Name: index_assessments_last_updated_timestamp; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_assessments_last_updated_timestamp ON public.assessments USING btree (last_updated_timestamp);


--
-- Name: index_assessments_run_id_created_timestamp; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_assessments_run_id_created_timestamp ON public.assessments USING btree (run_id, created_timestamp);


--
-- Name: index_assessments_trace_id_created_timestamp; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_assessments_trace_id_created_timestamp ON public.assessments USING btree (trace_id, created_timestamp);


--
-- Name: index_datasets_dataset_uuid; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_datasets_dataset_uuid ON public.datasets USING btree (dataset_uuid);


--
-- Name: index_datasets_experiment_id_dataset_source_type; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_datasets_experiment_id_dataset_source_type ON public.datasets USING btree (experiment_id, dataset_source_type);


--
-- Name: index_endpoint_model_mappings_endpoint_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_endpoint_model_mappings_endpoint_id ON public.endpoint_model_mappings USING btree (endpoint_id);


--
-- Name: index_endpoint_model_mappings_model_definition_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_endpoint_model_mappings_model_definition_id ON public.endpoint_model_mappings USING btree (model_definition_id);


--
-- Name: index_endpoint_tags_endpoint_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_endpoint_tags_endpoint_id ON public.endpoint_tags USING btree (endpoint_id);


--
-- Name: index_entity_associations_association_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_entity_associations_association_id ON public.entity_associations USING btree (association_id);


--
-- Name: index_entity_associations_reverse_lookup; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_entity_associations_reverse_lookup ON public.entity_associations USING btree (destination_type, destination_id, source_type, source_id);


--
-- Name: index_evaluation_dataset_records_dataset_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_evaluation_dataset_records_dataset_id ON public.evaluation_dataset_records USING btree (dataset_id);


--
-- Name: index_evaluation_dataset_tags_dataset_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_evaluation_dataset_tags_dataset_id ON public.evaluation_dataset_tags USING btree (dataset_id);


--
-- Name: index_evaluation_datasets_created_time; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_evaluation_datasets_created_time ON public.evaluation_datasets USING btree (created_time);


--
-- Name: index_evaluation_datasets_name; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_evaluation_datasets_name ON public.evaluation_datasets USING btree (name);


--
-- Name: index_inputs_destination_type_destination_id_source_type; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_inputs_destination_type_destination_id_source_type ON public.inputs USING btree (destination_type, destination_id, source_type);


--
-- Name: index_inputs_input_uuid; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_inputs_input_uuid ON public.inputs USING btree (input_uuid);


--
-- Name: index_issues_experiment_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_issues_experiment_id ON public.issues USING btree (experiment_id);


--
-- Name: index_issues_source_run_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_issues_source_run_id ON public.issues USING btree (source_run_id);


--
-- Name: index_issues_status; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_issues_status ON public.issues USING btree (status);


--
-- Name: index_jobs_name_status_creation_time; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_jobs_name_status_creation_time ON public.jobs USING btree (job_name, workspace, status, creation_time);


--
-- Name: index_latest_metrics_run_uuid; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_latest_metrics_run_uuid ON public.latest_metrics USING btree (run_uuid);


--
-- Name: index_logged_model_metrics_model_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_logged_model_metrics_model_id ON public.logged_model_metrics USING btree (model_id);


--
-- Name: index_metrics_run_uuid; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_metrics_run_uuid ON public.metrics USING btree (run_uuid);


--
-- Name: index_model_definitions_provider; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_model_definitions_provider ON public.model_definitions USING btree (provider);


--
-- Name: index_model_definitions_secret_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_model_definitions_secret_id ON public.model_definitions USING btree (secret_id);


--
-- Name: index_params_run_uuid; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_params_run_uuid ON public.params USING btree (run_uuid);


--
-- Name: index_scorer_versions_scorer_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_scorer_versions_scorer_id ON public.scorer_versions USING btree (scorer_id);


--
-- Name: index_scorers_experiment_id_scorer_name; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE UNIQUE INDEX index_scorers_experiment_id_scorer_name ON public.scorers USING btree (experiment_id, scorer_name);


--
-- Name: index_span_metrics_trace_id_span_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_span_metrics_trace_id_span_id ON public.span_metrics USING btree (trace_id, span_id);


--
-- Name: index_spans_experiment_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_spans_experiment_id ON public.spans USING btree (experiment_id);


--
-- Name: index_spans_experiment_id_duration; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_spans_experiment_id_duration ON public.spans USING btree (experiment_id, duration_ns);


--
-- Name: index_spans_experiment_id_status_type; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_spans_experiment_id_status_type ON public.spans USING btree (experiment_id, status, type);


--
-- Name: index_spans_experiment_id_type_status; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_spans_experiment_id_type_status ON public.spans USING btree (experiment_id, type, status);


--
-- Name: index_tags_run_uuid; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_tags_run_uuid ON public.tags USING btree (run_uuid);


--
-- Name: index_trace_info_experiment_id_timestamp_ms; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_trace_info_experiment_id_timestamp_ms ON public.trace_info USING btree (experiment_id, timestamp_ms);


--
-- Name: index_trace_metrics_request_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_trace_metrics_request_id ON public.trace_metrics USING btree (request_id);


--
-- Name: index_trace_request_metadata_request_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_trace_request_metadata_request_id ON public.trace_request_metadata USING btree (request_id);


--
-- Name: index_trace_tags_request_id; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE INDEX index_trace_tags_request_id ON public.trace_tags USING btree (request_id);


--
-- Name: unique_endpoint_model_linkage_mapping; Type: INDEX; Schema: public; Owner: mlflow
--

CREATE UNIQUE INDEX unique_endpoint_model_linkage_mapping ON public.endpoint_model_mappings USING btree (endpoint_id, model_definition_id, linkage_type);


--
-- Name: secrets prevent_secrets_aad_mutation; Type: TRIGGER; Schema: public; Owner: mlflow
--

CREATE TRIGGER prevent_secrets_aad_mutation BEFORE UPDATE ON public.secrets FOR EACH ROW EXECUTE FUNCTION public.prevent_secrets_aad_mutation();


--
-- Name: experiment_tags experiment_tags_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.experiment_tags
    ADD CONSTRAINT experiment_tags_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id);


--
-- Name: assessments fk_assessments_trace_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT fk_assessments_trace_id FOREIGN KEY (trace_id) REFERENCES public.trace_info(request_id) ON DELETE CASCADE;


--
-- Name: datasets fk_datasets_experiment_id_experiments; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT fk_datasets_experiment_id_experiments FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id) ON DELETE CASCADE;


--
-- Name: endpoint_bindings fk_endpoint_bindings_endpoint_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoint_bindings
    ADD CONSTRAINT fk_endpoint_bindings_endpoint_id FOREIGN KEY (endpoint_id) REFERENCES public.endpoints(endpoint_id) ON DELETE CASCADE;


--
-- Name: endpoint_model_mappings fk_endpoint_model_mappings_endpoint_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoint_model_mappings
    ADD CONSTRAINT fk_endpoint_model_mappings_endpoint_id FOREIGN KEY (endpoint_id) REFERENCES public.endpoints(endpoint_id) ON DELETE CASCADE;


--
-- Name: endpoint_model_mappings fk_endpoint_model_mappings_model_definition_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoint_model_mappings
    ADD CONSTRAINT fk_endpoint_model_mappings_model_definition_id FOREIGN KEY (model_definition_id) REFERENCES public.model_definitions(model_definition_id);


--
-- Name: endpoint_tags fk_endpoint_tags_endpoint_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoint_tags
    ADD CONSTRAINT fk_endpoint_tags_endpoint_id FOREIGN KEY (endpoint_id) REFERENCES public.endpoints(endpoint_id) ON DELETE CASCADE;


--
-- Name: endpoints fk_endpoints_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.endpoints
    ADD CONSTRAINT fk_endpoints_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id) ON DELETE SET NULL;


--
-- Name: evaluation_dataset_records fk_evaluation_dataset_records_dataset_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.evaluation_dataset_records
    ADD CONSTRAINT fk_evaluation_dataset_records_dataset_id FOREIGN KEY (dataset_id) REFERENCES public.evaluation_datasets(dataset_id) ON DELETE CASCADE;


--
-- Name: evaluation_dataset_tags fk_evaluation_dataset_tags_dataset_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.evaluation_dataset_tags
    ADD CONSTRAINT fk_evaluation_dataset_tags_dataset_id FOREIGN KEY (dataset_id) REFERENCES public.evaluation_datasets(dataset_id) ON DELETE CASCADE;


--
-- Name: issues fk_issues_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT fk_issues_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id) ON DELETE CASCADE;


--
-- Name: issues fk_issues_source_run_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.issues
    ADD CONSTRAINT fk_issues_source_run_id FOREIGN KEY (source_run_id) REFERENCES public.runs(run_uuid) ON DELETE SET NULL;


--
-- Name: logged_model_metrics fk_logged_model_metrics_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_metrics
    ADD CONSTRAINT fk_logged_model_metrics_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id);


--
-- Name: logged_model_metrics fk_logged_model_metrics_model_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_metrics
    ADD CONSTRAINT fk_logged_model_metrics_model_id FOREIGN KEY (model_id) REFERENCES public.logged_models(model_id) ON DELETE CASCADE;


--
-- Name: logged_model_metrics fk_logged_model_metrics_run_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_metrics
    ADD CONSTRAINT fk_logged_model_metrics_run_id FOREIGN KEY (run_id) REFERENCES public.runs(run_uuid) ON DELETE CASCADE;


--
-- Name: logged_model_params fk_logged_model_params_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_params
    ADD CONSTRAINT fk_logged_model_params_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id);


--
-- Name: logged_model_params fk_logged_model_params_model_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_params
    ADD CONSTRAINT fk_logged_model_params_model_id FOREIGN KEY (model_id) REFERENCES public.logged_models(model_id) ON DELETE CASCADE;


--
-- Name: logged_model_tags fk_logged_model_tags_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_tags
    ADD CONSTRAINT fk_logged_model_tags_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id);


--
-- Name: logged_model_tags fk_logged_model_tags_model_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_model_tags
    ADD CONSTRAINT fk_logged_model_tags_model_id FOREIGN KEY (model_id) REFERENCES public.logged_models(model_id) ON DELETE CASCADE;


--
-- Name: logged_models fk_logged_models_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.logged_models
    ADD CONSTRAINT fk_logged_models_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id) ON DELETE CASCADE;


--
-- Name: model_definitions fk_model_definitions_secret_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.model_definitions
    ADD CONSTRAINT fk_model_definitions_secret_id FOREIGN KEY (secret_id) REFERENCES public.secrets(secret_id) ON DELETE SET NULL;


--
-- Name: model_version_tags fk_model_version_tags_model_versions; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.model_version_tags
    ADD CONSTRAINT fk_model_version_tags_model_versions FOREIGN KEY (workspace, name, version) REFERENCES public.model_versions(workspace, name, version) ON UPDATE CASCADE;


--
-- Name: model_versions fk_model_versions_registered_models; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT fk_model_versions_registered_models FOREIGN KEY (workspace, name) REFERENCES public.registered_models(workspace, name) ON UPDATE CASCADE;


--
-- Name: online_scoring_configs fk_online_scoring_configs_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.online_scoring_configs
    ADD CONSTRAINT fk_online_scoring_configs_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id);


--
-- Name: online_scoring_configs fk_online_scoring_configs_scorer_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.online_scoring_configs
    ADD CONSTRAINT fk_online_scoring_configs_scorer_id FOREIGN KEY (scorer_id) REFERENCES public.scorers(scorer_id) ON DELETE CASCADE;


--
-- Name: registered_model_aliases fk_registered_model_aliases_registered_models; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.registered_model_aliases
    ADD CONSTRAINT fk_registered_model_aliases_registered_models FOREIGN KEY (workspace, name) REFERENCES public.registered_models(workspace, name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: registered_model_tags fk_registered_model_tags_registered_models; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.registered_model_tags
    ADD CONSTRAINT fk_registered_model_tags_registered_models FOREIGN KEY (workspace, name) REFERENCES public.registered_models(workspace, name) ON UPDATE CASCADE;


--
-- Name: scorer_versions fk_scorer_versions_scorer_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.scorer_versions
    ADD CONSTRAINT fk_scorer_versions_scorer_id FOREIGN KEY (scorer_id) REFERENCES public.scorers(scorer_id) ON DELETE CASCADE;


--
-- Name: scorers fk_scorers_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.scorers
    ADD CONSTRAINT fk_scorers_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id) ON DELETE CASCADE;


--
-- Name: span_metrics fk_span_metrics_span; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.span_metrics
    ADD CONSTRAINT fk_span_metrics_span FOREIGN KEY (trace_id, span_id) REFERENCES public.spans(trace_id, span_id) ON DELETE CASCADE;


--
-- Name: spans fk_spans_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.spans
    ADD CONSTRAINT fk_spans_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id);


--
-- Name: spans fk_spans_trace_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.spans
    ADD CONSTRAINT fk_spans_trace_id FOREIGN KEY (trace_id) REFERENCES public.trace_info(request_id) ON DELETE CASCADE;


--
-- Name: trace_info fk_trace_info_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.trace_info
    ADD CONSTRAINT fk_trace_info_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id);


--
-- Name: trace_metrics fk_trace_metrics_request_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.trace_metrics
    ADD CONSTRAINT fk_trace_metrics_request_id FOREIGN KEY (request_id) REFERENCES public.trace_info(request_id) ON DELETE CASCADE;


--
-- Name: trace_request_metadata fk_trace_request_metadata_request_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.trace_request_metadata
    ADD CONSTRAINT fk_trace_request_metadata_request_id FOREIGN KEY (request_id) REFERENCES public.trace_info(request_id) ON DELETE CASCADE;


--
-- Name: trace_tags fk_trace_tags_request_id; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.trace_tags
    ADD CONSTRAINT fk_trace_tags_request_id FOREIGN KEY (request_id) REFERENCES public.trace_info(request_id) ON DELETE CASCADE;


--
-- Name: latest_metrics latest_metrics_run_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.latest_metrics
    ADD CONSTRAINT latest_metrics_run_uuid_fkey FOREIGN KEY (run_uuid) REFERENCES public.runs(run_uuid);


--
-- Name: metrics metrics_run_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.metrics
    ADD CONSTRAINT metrics_run_uuid_fkey FOREIGN KEY (run_uuid) REFERENCES public.runs(run_uuid);


--
-- Name: params params_run_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.params
    ADD CONSTRAINT params_run_uuid_fkey FOREIGN KEY (run_uuid) REFERENCES public.runs(run_uuid);


--
-- Name: runs runs_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiments(experiment_id);


--
-- Name: tags tags_run_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_run_uuid_fkey FOREIGN KEY (run_uuid) REFERENCES public.runs(run_uuid);


--
-- Name: webhook_events webhook_events_webhook_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mlflow
--

ALTER TABLE ONLY public.webhook_events
    ADD CONSTRAINT webhook_events_webhook_id_fkey FOREIGN KEY (webhook_id) REFERENCES public.webhooks(webhook_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict ZEmC1pns6SIX2XrKjgvmjzyWF8FrxygF8xe08ttffIWLlofXFUh1ewJuaeGFdgN

