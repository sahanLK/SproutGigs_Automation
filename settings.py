"""
This file contains some constant variables that can be used to modify
application behaviour without touching the application code directly.
"""


"""
What to do when code submission jobs found. [Options]: [skip | hide]
"""
CODE_SUBMIT_JOBS = 'skip'

"""
Skip jobs that require history page screenshot submissions.
"""
SKIP_SNAPSHOT_REQ_JOBS = False

"""
Use custom existing ad site data, when programme failed to find the ad data in the site
"""
ALTERNATE_AD_DATA = True

"""
Take the history page screenshot automatically after filling all the proofs.
"""
AUTO_PICK_SNAPSHOT = True
