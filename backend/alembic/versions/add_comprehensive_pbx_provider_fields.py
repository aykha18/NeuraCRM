"""Add comprehensive PBX provider configuration fields

Revision ID: add_comprehensive_pbx_provider_fields
Revises: 
Create Date: 2024-12-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_pbx_fields'
down_revision = '7f8e9d0c1b2a'  # Latest existing migration
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to pbx_providers table
    op.add_column('pbx_providers', sa.Column('authentication_name', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('enable_outbound_proxy', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('outbound_proxy_host', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('outbound_proxy_port', sa.Integer(), nullable=True, default=5060))
    op.add_column('pbx_providers', sa.Column('transport', sa.String(), nullable=True, default='UDP'))
    op.add_column('pbx_providers', sa.Column('enable_nat_traversal', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('nat_type', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('local_network', sa.String(), nullable=True))
    
    # Trunk Configuration
    op.add_column('pbx_providers', sa.Column('trunk_type', sa.String(), nullable=True, default='register'))
    op.add_column('pbx_providers', sa.Column('register_interval', sa.Integer(), nullable=True, default=3600))
    op.add_column('pbx_providers', sa.Column('register_timeout', sa.Integer(), nullable=True, default=20))
    op.add_column('pbx_providers', sa.Column('max_retries', sa.Integer(), nullable=True, default=5))
    
    # SIP Settings
    op.add_column('pbx_providers', sa.Column('sip_context', sa.String(), nullable=True, default='default'))
    op.add_column('pbx_providers', sa.Column('from_domain', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('to_domain', sa.String(), nullable=True))
    
    # DID/DDI Configuration
    op.add_column('pbx_providers', sa.Column('did_numbers', sa.Text(), nullable=True))
    op.add_column('pbx_providers', sa.Column('did_pattern', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('did_strip_digits', sa.Integer(), nullable=True, default=0))
    
    # Caller ID Reformatting
    op.add_column('pbx_providers', sa.Column('inbound_caller_id_reformatting', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('outbound_caller_id_reformatting', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('caller_id_prefix', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('caller_id_suffix', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('caller_id_replacement_rules', sa.Text(), nullable=True))
    
    # SIP Headers
    op.add_column('pbx_providers', sa.Column('custom_sip_headers', sa.Text(), nullable=True))
    op.add_column('pbx_providers', sa.Column('p_asserted_identity', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('remote_party_id', sa.String(), nullable=True))
    
    # Codec Settings
    op.add_column('pbx_providers', sa.Column('preferred_codecs', sa.Text(), nullable=True))
    op.add_column('pbx_providers', sa.Column('codec_negotiation', sa.String(), nullable=True, default='negotiate'))
    op.add_column('pbx_providers', sa.Column('dtmf_mode', sa.String(), nullable=True, default='rfc2833'))
    
    # Quality of Service (QoS)
    op.add_column('pbx_providers', sa.Column('enable_qos', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('dscp_value', sa.Integer(), nullable=True, default=46))
    op.add_column('pbx_providers', sa.Column('bandwidth_limit', sa.Integer(), nullable=True))
    
    # Security Settings
    op.add_column('pbx_providers', sa.Column('enable_srtp', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('srtp_mode', sa.String(), nullable=True, default='optional'))
    op.add_column('pbx_providers', sa.Column('enable_tls', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('tls_cert_path', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('tls_key_path', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('tls_ca_path', sa.String(), nullable=True))
    
    # Advanced Settings
    op.add_column('pbx_providers', sa.Column('call_forwarding_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('pbx_providers', sa.Column('call_waiting_enabled', sa.Boolean(), nullable=True, default=True))
    op.add_column('pbx_providers', sa.Column('three_way_calling_enabled', sa.Boolean(), nullable=True, default=True))
    
    # Monitoring and Analytics
    op.add_column('pbx_providers', sa.Column('enable_call_monitoring', sa.Boolean(), nullable=True, default=True))
    op.add_column('pbx_providers', sa.Column('enable_call_recording', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('recording_format', sa.String(), nullable=True, default='wav'))
    op.add_column('pbx_providers', sa.Column('recording_quality', sa.String(), nullable=True, default='high'))
    
    # Webhook Settings
    op.add_column('pbx_providers', sa.Column('webhook_events', sa.Text(), nullable=True))
    
    # API Integration
    op.add_column('pbx_providers', sa.Column('api_endpoint', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('api_secret', sa.String(), nullable=True))
    op.add_column('pbx_providers', sa.Column('api_version', sa.String(), nullable=True, default='v1'))
    
    # Status and Settings
    op.add_column('pbx_providers', sa.Column('failover_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('pbx_providers', sa.Column('failover_provider_id', sa.Integer(), nullable=True))
    op.add_column('pbx_providers', sa.Column('last_registration', sa.DateTime(), nullable=True))
    op.add_column('pbx_providers', sa.Column('registration_status', sa.String(), nullable=True, default='unknown'))
    
    # Add foreign key constraint for failover_provider_id
    op.create_foreign_key(
        'fk_pbx_providers_failover_provider',
        'pbx_providers', 'pbx_providers',
        ['failover_provider_id'], ['id']
    )
    
    # Update existing records with default values
    op.execute("""
        UPDATE pbx_providers SET 
            enable_outbound_proxy = false,
            outbound_proxy_port = 5060,
            transport = 'UDP',
            enable_nat_traversal = false,
            trunk_type = 'register',
            register_interval = 3600,
            register_timeout = 20,
            max_retries = 5,
            sip_context = 'default',
            did_strip_digits = 0,
            inbound_caller_id_reformatting = false,
            outbound_caller_id_reformatting = false,
            codec_negotiation = 'negotiate',
            dtmf_mode = 'rfc2833',
            enable_qos = false,
            dscp_value = 46,
            enable_srtp = false,
            srtp_mode = 'optional',
            enable_tls = false,
            call_forwarding_enabled = true,
            call_waiting_enabled = true,
            three_way_calling_enabled = true,
            enable_call_monitoring = true,
            enable_call_recording = false,
            recording_format = 'wav',
            recording_quality = 'high',
            api_version = 'v1',
            failover_enabled = false,
            registration_status = 'unknown'
        WHERE id IS NOT NULL;
    """)


def downgrade():
    # Drop foreign key constraint
    op.drop_constraint('fk_pbx_providers_failover_provider', 'pbx_providers', type_='foreignkey')
    
    # Drop all the added columns
    op.drop_column('pbx_providers', 'registration_status')
    op.drop_column('pbx_providers', 'last_registration')
    op.drop_column('pbx_providers', 'failover_provider_id')
    op.drop_column('pbx_providers', 'failover_enabled')
    op.drop_column('pbx_providers', 'api_version')
    op.drop_column('pbx_providers', 'api_secret')
    op.drop_column('pbx_providers', 'api_endpoint')
    op.drop_column('pbx_providers', 'webhook_events')
    op.drop_column('pbx_providers', 'recording_quality')
    op.drop_column('pbx_providers', 'recording_format')
    op.drop_column('pbx_providers', 'enable_call_recording')
    op.drop_column('pbx_providers', 'enable_call_monitoring')
    op.drop_column('pbx_providers', 'three_way_calling_enabled')
    op.drop_column('pbx_providers', 'call_waiting_enabled')
    op.drop_column('pbx_providers', 'call_forwarding_enabled')
    op.drop_column('pbx_providers', 'tls_ca_path')
    op.drop_column('pbx_providers', 'tls_key_path')
    op.drop_column('pbx_providers', 'tls_cert_path')
    op.drop_column('pbx_providers', 'enable_tls')
    op.drop_column('pbx_providers', 'srtp_mode')
    op.drop_column('pbx_providers', 'enable_srtp')
    op.drop_column('pbx_providers', 'bandwidth_limit')
    op.drop_column('pbx_providers', 'dscp_value')
    op.drop_column('pbx_providers', 'enable_qos')
    op.drop_column('pbx_providers', 'dtmf_mode')
    op.drop_column('pbx_providers', 'codec_negotiation')
    op.drop_column('pbx_providers', 'preferred_codecs')
    op.drop_column('pbx_providers', 'remote_party_id')
    op.drop_column('pbx_providers', 'p_asserted_identity')
    op.drop_column('pbx_providers', 'custom_sip_headers')
    op.drop_column('pbx_providers', 'caller_id_replacement_rules')
    op.drop_column('pbx_providers', 'caller_id_suffix')
    op.drop_column('pbx_providers', 'caller_id_prefix')
    op.drop_column('pbx_providers', 'outbound_caller_id_reformatting')
    op.drop_column('pbx_providers', 'inbound_caller_id_reformatting')
    op.drop_column('pbx_providers', 'did_strip_digits')
    op.drop_column('pbx_providers', 'did_pattern')
    op.drop_column('pbx_providers', 'did_numbers')
    op.drop_column('pbx_providers', 'to_domain')
    op.drop_column('pbx_providers', 'from_domain')
    op.drop_column('pbx_providers', 'sip_context')
    op.drop_column('pbx_providers', 'max_retries')
    op.drop_column('pbx_providers', 'register_timeout')
    op.drop_column('pbx_providers', 'register_interval')
    op.drop_column('pbx_providers', 'trunk_type')
    op.drop_column('pbx_providers', 'local_network')
    op.drop_column('pbx_providers', 'nat_type')
    op.drop_column('pbx_providers', 'enable_nat_traversal')
    op.drop_column('pbx_providers', 'transport')
    op.drop_column('pbx_providers', 'outbound_proxy_port')
    op.drop_column('pbx_providers', 'outbound_proxy_host')
    op.drop_column('pbx_providers', 'enable_outbound_proxy')
    op.drop_column('pbx_providers', 'authentication_name')
