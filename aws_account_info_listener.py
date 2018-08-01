"""Listens for aws account info requests."""

import logging as log

import handlers.aws_info_getter as aws_info_getter
from glom import glom

FORMAT = ("[%(asctime)s][%(levelname)s]" +
          "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
log.basicConfig(filename='terrasnow_enterprise.log', level=log.INFO,
                format=FORMAT)


def event_listener(request):
    """Process aws account information request."""
    log.info('recieved request: {}'.format(request))
    region = glom(request, 'data.0.region', default=False)
    if not region:
        log.error("region not found in request")
        return "ERROR: region not provided"
    arn = glom(request, 'data.0.arn', default=False)
    if not arn:
        log.error("arn not found in request")
        return "ERROR: arn not prvoided"
    duration = glom(request, 'data.0.duration', default=False)
    if duration:
        duration = int(duration)
    else:
        log.error("duration not found in request")
        return "ERROR: duration not provided"
    info_request = aws_info_getter.AwsInfoGetter(region=region,
                                                 role_to_assume_arn=arn,
                                                 duration=duration)
    return info_request.assumed_role_get_everything()
