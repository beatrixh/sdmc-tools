LDMS_PATH_HVTN = '/data/pipelines/fstrf-ldms-postimport/hvtn/hvtn.csdb.csv'
LDMS_PATH_COVPN = '/data/pipelines/fstrf-ldms-postimport/covpn/covpn.csdb.csv'
FAKE_LDMS = '/networks/vtn/lab/SDMC_labscience/operations/documents/templates/assay/template_testing/process_testing/generated_ldms.csv'

LDMS_COLUMNS = [
    'labid', 'lims', 'parusp', 'uspeci', 'clasid', 'patid', 'txtpid',
    'drawdm', 'drawdd', 'drawdy', 'recdtm', 'recdtd', 'recdty', 'drawth',
    'drawtm', 'rec_tm', 'vidval', 'vidstr', 'lstudy', 'id3', 'guspec',
    'specid', 'sec_id', 'primstr', 'addstr', 'dervstr', 'dervst2', 'sec_tp',
    'rlprot', 'volume', 'volstr', 'privol', 'pvlunt', 'proctm', 'procdm',
    'procdd', 'procdy', 'ptinit', 'frzdtm', 'frzdtd', 'frzdty', 'froztm',
    'cellct', 'condstr', 'cond2', 'noprot', 'avalbl', 'addtim', 'addunt',
    'stored', 'stordm', 'stordd', 'stordy', 'sttemp', 'shipfg', 'tolab',
    'shipno', 'shptmp', 'shipdm', 'shipdd', 'shipdy', 'frlab', 'rb_no',
    'rcvtmp', 'recvdm', 'recvdd', 'recvdy', 'clinic', 'commts', 'logtyp',
    'creas', 'cxtype', 'cxuspe', 'cxdatm', 'cxdatd', 'cxdaty', 'defund',
    'frzer', 'level1', 'level2', 'contai', 'posit', 'conhum', 'conoth',
    'sysdte', 'ldchng'
]

STANDARD_COLS = [
    'txtpid', 'drawdm', 'drawdd', 'drawdy',
    'vidval', 'lstudy', 'guspec', 'primstr', 'addstr', 'dervstr'
]

LDMS_RELABEL_DICT = {
    'txtpid': 'ptid',
    'drawdm': 'drawdm',
    'drawdd': 'drawdd',
    'drawdy': 'drawdy',
    'vidval': 'visitno',
    'lstudy': 'protocol',
    'guspec': 'guspec',
    'primstr': 'spec_primary',
    'addstr': 'spec_additive',
    'dervstr': 'spec_derivative',
}

SPEC_TYPE_DEFN_MAP = {
    ('BLD','PLA'): 'Plasma',
    ('BLD','SER'): 'Serum',
    ('REC','SPG'): 'Rectal Sponge',
    ('REC','SUP'): 'Rectal Biopsy',
    ('CER','SPG'): 'Cervical Sponge',
    ('CER','SUP'): 'Cervical Biopsy',
    ('VAG','SUP'): 'Vaginal Biopsy',
    ('VAG','WCK'): 'Vaginal Weck',
    ('SAL','FLD'): 'Saliva',
    ('SAL','SAL'): 'Saliva',
    ('SEM','SEM'): 'Semen',
    ('SEM','FLD'): 'Semen',
    ('BLD','CEL'): 'PBMC',
    ('BLD', 'CSR'): 'Serum',
    ('BLD', 'DBS'): 'Dried Blood Spot',
    ('BLD', 'LYS'): 'Whole Blood (Lysed)',
    ('VCS', 'FLD'): 'Cervicovaginal Secretions (Fluid)',
    ('VCS', 'MUC'): 'Cervicovaginal Secretions (Mucus)',
    ('VAG', 'SWB'): 'Vaginal Swab',
    ('BLD', 'BLD'): 'Whole Blood',
    ('VCS', "N/A"): 'Cervicovaginal Secretions',
    ('BLD', "N/A"): 'Whole Blood',
    ('VCS', 'SWB'): 'Cervicovaginal Secretions (Swab)',
    ('REC', 'BPS'): 'Rectal Biopsy',
    ('VAG', 'BPS'): 'Vaginal Biopsy',
    ('CER', 'BPS'): 'Cervical Biopsy',
    ('REC', 'SEC'): 'Rectal Secretions'
}

STD_PREFACE_COLS = [
    'network',
    'protocol',
    'specrole',
    'guspec',
    'ptid',
    'visitno',
    'drawdt',
    'spectype',
    'spec_primary',
    'spec_additive',
    'spec_derivative',
    'upload_lab_id',
    'assay_lab_name',
    'assay_type',
    'assay_subtype',
    'assay_kit',
    'instrument',
]

STD_POSTFACE_COLS = [
    'sdmc_processing_datetime',
    'sdmc_data_receipt_datetime',
    'input_file_name'
]
