PROFILE = 'profile-recensio.theme:default'


def v1to2(portal_setup):
    portal_setup.runImportStepFromProfile(PROFILE, 'jsregistry')
