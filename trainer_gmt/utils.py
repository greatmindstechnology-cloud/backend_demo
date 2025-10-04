# trainer_gmt/utils.py
import logging
from datetime import datetime, timedelta
from django.conf import settings
import jwt  # Install: pip install pyjwt

logger = logging.getLogger(__name__)

# def create_jitsi_meeting(student_email, counselor_email, session_time, domain):
#     """Create a Jitsi Meet meeting link."""
#     try:
#         # Generate a unique room name
#         room_name = f'gmt-counseling-{session_time.isoformat().replace(":", "-")}-{domain.replace(" ", "-").lower()}'
#         jitsi_server = getattr(settings, 'JITSI_SERVER_URL', 'https://meet.jit.si')
        
#         # Generate JWT token for secure rooms (optional, for self-hosted Jitsi with JWT enabled)
#         if hasattr(settings, 'JITSI_APP_ID') and hasattr(settings, 'JITSI_SECRET'):
#             payload = {
#                 'context': {
#                     'user': {
#                         'email': counselor_email,
#                         'name': 'Counselor',
#                         'moderator': True  # Grant moderator rights to counselor
#                     },
#                     'group': 'gmt-counseling'
#                 },
#                 'aud': 'jitsi',
#                 'iss': settings.JITSI_APP_ID,
#                 'sub': jitsi_server.replace('https://', ''),
#                 'room': room_name,
#                 'exp': int((session_time + timedelta(hours=1)).timestamp())
#             }
#             token = jwt.encode(payload, settings.JITSI_SECRET, algorithm='HS256')
#             meet_link = f'{jitsi_server}/{room_name}?jwt={token}'
#         else:
#             # Public Jitsi server (meet.jit.si) or self-hosted without JWT
#             meet_link = f'{jitsi_server}/{room_name}'
        
#         return room_name, meet_link
#     except Exception as e:
#         logger.error(f"Failed to create Jitsi meeting: {str(e)}")
#         raise

def create_jitsi_meeting(student_email, counselor_email, session_time, domain):
    """Create a Jitsi Meet meeting link for meet.jit.si."""
    try:
        room_name = f'gmt-counseling-{session_time.isoformat().replace(":", "-")}-{domain.replace(" ", "-").lower()}'
        jitsi_server = getattr(settings, 'JITSI_SERVER_URL', 'https://meet.jit.si')
        meet_link = f'{jitsi_server}/{room_name}'
        return room_name, meet_link
    except Exception as e:
        logger.error(f"Failed to create Jitsi meeting: {str(e)}")
        raise