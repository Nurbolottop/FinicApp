# Manual migration for FCMDeviceToken table only

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS base_fcmdevicetoken (
                    id SERIAL PRIMARY KEY,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    device_type VARCHAR(10) DEFAULT 'android' NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS base_fcmdevicetoken_user_id_idx ON base_fcmdevicetoken(user_id);
                CREATE INDEX IF NOT EXISTS base_fcmdevicetoken_token_idx ON base_fcmdevicetoken(token);
            """,
            reverse_sql="DROP TABLE IF EXISTS base_fcmdevicetoken;",
        ),
    ]

