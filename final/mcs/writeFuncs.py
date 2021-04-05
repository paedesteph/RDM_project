#
# A "WriteFunc" is called after substituting parameter values, before
# writing modified files, per Monte Carlo trial.
#
import pandas as pd

from pygcam.config import getParam
from pygcam.utils import pathjoin
from pygcam.log import getLogger
#from pygcam.error import SetupException
from pygcam.xmlEditor import xmlEdit
from pygcam.XMLFile import McsValues

# unique name so log level is configurable in .pygcam.cfg
_logger = getLogger('ord.writeFuncs')

# TBD: Pass as kwargs to writeFuncs; need to update API docs
GROUP = ''          # directories do not include group name
BASELINE = 'mcs'

# Strategy
#
# - Allow config file itself to have a write func? Nah, need a per-trial version.
# - Copy config.xml to "exe" dir and modify it as the scenarios.xml file would have done.
# - Modify project.xml to call "gcam" step with "-C config.xml" so it takes it from exe dir.
#
# - Would it work as <InputFile name="../local-xml/base/config.xml"> ?
#   Might need special tag like <InputFile name="__config__"> or a new tag,
#   <ConfigFile>
#       <WriteFunc>writeFuncs.configure</WriteFunc>
#   </ConfigFile>

def createScenario(inputFile, xmlFile, trialDir):
    basedir    = pathjoin(trialDir, 'trial-xml', 'local-xml', GROUP, BASELINE)
    valuesFile = pathjoin(basedir, 'mcsValues.xml')

    # This requires that mcsValues.xml is updated before the func is called, so
    # the <InputFile> specifying the "writeFunc" must come after mcsValues.xml.
    mcsValues = McsValues(valuesFile)

    value_names = {
        'pop'     : None,               # "pop" values are 2 and 5, used directly

        'dds'     : ['A2', 'constant'], # for other params, values are 0 or 1, used as indices
        'cons_dem': ['ref', 'high'],
        'ccs'     : ['ref', 'no'],
        're'      : ['ref', 'adv'],
        'bev'     : ['ref', 'adv'],
        'nuc_ret' : ['ref', 'fast']
    }

    def value_by_name(param):
        value = int(mcsValues.valueForRegion(param, 'global'))  # all values are int, though MCS system renders as floats
        names = value_names[param]
        return value if names is None else names[value]         # use trial value as index into names list

    # copy the trial values for these parameters into a dictionary keyed by param name
    v = {param : value_by_name(param) for param in value_names.keys()}

    pop = v['pop']
    dds = v['dds']
    ccs = v['ccs']
    re  = v['re']
    bev = v['bev']
    cons_dem = v['cons_dem']
    nuc_ret = v['nuc_ret']

    # construct a mnemonic scenario name
    scenario = f"SSP{pop}-CI{dds}-CD{cons_dem}-CCS{ccs}-RE{re}-BEV{bev}-NUC{nuc_ret}"
    _logger.info("(writeFunc) running scenario '%s'", scenario)


    # tree = xmlFile.tree     # useful IFF tree refers to config.xml

    from pygcam.mcs.XMLConfigFile import XMLConfigFile, COMPONENTS_GROUP
    # from pygcam.xmlEditor import xmlEdit

    # context = 'whatever'
    # cfg = XMLConfigFile.getConfigForScenario(context, useCopy=False)

    # Or this?
    from pygcam.xmlSetup import scenarioEditor

    xmlSrcDir = getParam('GCAM.XmlSrc')         # or is it a subdir of this that we need?
    refWorkspace = getParam('MCS.RunWorkspace')
    ed = scenarioEditor('mcs', baseline='mcs', xmlSrcDir=xmlSrcDir, refWorkspace=refWorkspace, mcsMode='trial')
    cfg_path = ed.cfgPath()
    print(f"writeFuncs.py: config path is {cfg_path}")

    # ed.addScenarioComponent(name, pathname)
    # cfg.insertComponentPathname(name, pathname, after)
    # cfg.updateComponentPathname(name, pathname)
    # cfg.deleteComponent(name)


    # <add name="SSP">../input/policy/scenarios/pop_gdp_{pop}.xml</add>
    ed.addScenarioComponent("SSP", f"../input/policy/scenarios/pop_gdp_{pop}.xml")

    # <replace name="dd_usa">../input/policy/scenarios/HDDCDD_{dds}.xml</replace>
    ed.updateScenarioComponent("dd_usa", f"../input/policy/scenarios/HDDCDD_{dds}.xml")

    # <add name="trn_pe_zero">../input/policy/scenarios/trn_pe_zero.xml</add>
    # <add name="trn_dem">../input/policy/scenarios/td_{pop}_{cons_dem}.xml</add>
    # <add name="FLSP">../input/policy/scenarios/FLSP_{pop}_{cons_dem}.xml</add>
    ed.addScenarioComponent("trn_pe_zero", "../input/policy/scenarios/trn_pe_zero.xml")
    ed.addScenarioComponent("trn_dem",    f"../input/policy/scenarios/td_{pop}_{cons_dem}.xml")
    ed.addScenarioComponent("FLSP",       f"../input/policy/scenarios/FLSP_{pop}_{cons_dem}.xml")

    # 			<if value1="{ccs}" value2="no">
    # 					<add name="noccs_st">../input/policy/scenarios/noccs_st.xml</add>
    # 					<add name="noccs_pt">../input/policy/scenarios/noccs_pt.xml</add>
    # 			</if>
    if ccs == "no":
        ed.addScenarioComponent("noccs_st", "../input/policy/scenarios/noccs_st.xml")
        ed.addScenarioComponent("noccs_pt", "../input/policy/scenarios/noccs_pt.xml")

    # 			<if value1="{re}" value2="adv">
    # 					<add name="re_adv">../input/policy/scenarios/adv_re_tech.xml</add>
    # 			</if>
    if re == "adv":
        ed.addScenarioComponent("re_adv", "../input/policy/scenarios/adv_re_tech.xml")

    # 			<if value1="{bev}" value2="adv">
    # 					<replace name="bev_UCD">../input/policy/scenarios/bev_UCD_adv.xml</replace>
    # 					<insert name="bev_USA_adv" after="bev_USA">../input/policy/scenarios/bev_USA_adv.xml</insert>
    # 					<add name="BEV_LoBatt_compact">../input/policy/reference/BEV_LoBatt_compact_wLearning.xml</add>
    # 					<add name="BEV_LoBatt_large">../input/policy/reference/BEV_LoBatt_large_wLearning.xml</add>
    # 					<add name="BEV_LoBatt_lttruck_SUV">../input/policy/reference/BEV_LoBatt_lttruck_SUV_wLearning.xml</add>
    # 					<add name="BEV_LoBatt_midsize">../input/policy/reference/BEV_LoBatt_midsize_wLearning.xml</add>
    # 					<add name="BEV_LDV_SW">../input/policy/reference/BEV_SW_update-global.xml</add>
    # 			</if>
    if bev == "adv":
        ed.updateScenarioComponent("bev_UCD",     "../input/policy/scenarios/bev_UCD_adv.xml")
        ed.insertScenarioComponent("bev_USA_adv", "../input/policy/scenarios/bev_USA_adv.xml", "bev_USA")

        ed.addScenarioComponent("BEV_LoBatt_compact",     "../input/policy/reference/BEV_LoBatt_compact_wLearning.xml")
        ed.addScenarioComponent("BEV_LoBatt_large",       "../input/policy/reference/BEV_LoBatt_large_wLearning.xml")
        ed.addScenarioComponent("BEV_LoBatt_lttruck_SUV", "../input/policy/reference/BEV_LoBatt_lttruck_SUV_wLearning.xml")
        ed.addScenarioComponent("BEV_LoBatt_midsize",     "../input/policy/reference/BEV_LoBatt_midsize_wLearning.xml")
        ed.addScenarioComponent("BEV_LDV_SW",             "../input/policy/reference/BEV_SW_update-global.xml")

    # 			<if value1="{nuc_ret}" value2="fast">
    # 					<function name="multiply">tag="nuc_usa",xpath="//half-life",value=0.6</function>
    # 					<add name="nuc_bound">../input/policy/scenarios/nonewnuclear.xml</add>
    # 			</if>

    if nuc_ret == "fast":
        # <function name="multiply">tag="nuc_usa",xpath="//half-life",value=0.6</function>
        ed.multiply("nuc_usa", "//half-life", 0.6)
        ed.addScenarioComponent("nuc_bound", "../input/policy/scenarios/nonewnuclear.xml")

    cfg.write(path=configPath)
