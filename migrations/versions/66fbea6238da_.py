"""Add end users and relevant indices as well as an index to orgs.api_key

Revision ID: 66fbea6238da
Revises: 26afe8245b5e
Create Date: 2018-07-15 20:00:24.997638

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '66fbea6238da'
down_revision = '26afe8245b5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('end_users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('email', sa.String(length=90), nullable=True),
    sa.Column('phone_number', sa.String(length=50), nullable=True),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['orgs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_end_users_email'), 'end_users', ['email'], unique=True)
    op.create_index(op.f('ix_end_users_phone_number'), 'end_users', ['phone_number'], unique=True)
    op.create_table('end_users_email_auth_token',
    sa.Column('token', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('end_user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expired_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('sent', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['end_user_id'], ['end_users.id'], ),
    sa.PrimaryKeyConstraint('token', 'end_user_id')
    )
    op.create_index(op.f('ix_end_users_email_auth_token_active'), 'end_users_email_auth_token', ['active'], unique=False)
    op.create_index(op.f('ix_end_users_email_auth_token_sent'), 'end_users_email_auth_token', ['sent'], unique=False)
    op.create_table('end_users_sms_auth_token',
    sa.Column('token', sa.String(length=6), nullable=False),
    sa.Column('end_user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expired_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('sent', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['end_user_id'], ['end_users.id'], ),
    sa.PrimaryKeyConstraint('token', 'end_user_id')
    )
    op.create_index(op.f('ix_end_users_sms_auth_token_active'), 'end_users_sms_auth_token', ['active'], unique=False)
    op.create_index(op.f('ix_end_users_sms_auth_token_sent'), 'end_users_sms_auth_token', ['sent'], unique=False)
    op.create_index(op.f('ix_orgs_client_id'), 'orgs', ['client_id'], unique=True)
    op.create_index(op.f('ix_orgs_client_secret'), 'orgs', ['client_secret'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_orgs_client_id'), table_name='orgs')
    op.drop_index(op.f('ix_orgs_client_secret'), table_name='orgs')
    op.drop_index(op.f('ix_end_users_sms_auth_token_sent'), table_name='end_users_sms_auth_token')
    op.drop_index(op.f('ix_end_users_sms_auth_token_active'), table_name='end_users_sms_auth_token')
    op.drop_table('end_users_sms_auth_token')
    op.drop_index(op.f('ix_end_users_email_auth_token_sent'), table_name='end_users_email_auth_token')
    op.drop_index(op.f('ix_end_users_email_auth_token_active'), table_name='end_users_email_auth_token')
    op.drop_table('end_users_email_auth_token')
    op.drop_index(op.f('ix_end_users_phone_number'), table_name='end_users')
    op.drop_index(op.f('ix_end_users_email'), table_name='end_users')
    op.drop_table('end_users')
    # ### end Alembic commands ###
