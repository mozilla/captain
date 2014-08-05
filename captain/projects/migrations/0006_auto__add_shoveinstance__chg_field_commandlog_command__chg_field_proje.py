# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShoveInstance'
        db.create_table(u'projects_shoveinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('routing_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_heartbeat', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
        ))
        db.send_create_signal(u'projects', ['ShoveInstance'])


        # Changing field 'CommandLog.command'
        db.alter_column(u'projects_commandlog', 'command', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Project.project_name'
        db.alter_column(u'projects_project', 'project_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255))
        # Adding unique constraint on 'Project', fields ['project_name']
        db.create_unique(u'projects_project', ['project_name'])


        # Changing field 'Project.name'
        db.alter_column(u'projects_project', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Project.queue'
        db.alter_column(u'projects_project', 'queue', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'ScheduledCommand.command'
        db.alter_column(u'projects_scheduledcommand', 'command', self.gf('django.db.models.fields.CharField')(max_length=255))

    def backwards(self, orm):
        # Removing unique constraint on 'Project', fields ['project_name']
        db.delete_unique(u'projects_project', ['project_name'])

        # Deleting model 'ShoveInstance'
        db.delete_table(u'projects_shoveinstance')


        # Changing field 'CommandLog.command'
        db.alter_column(u'projects_commandlog', 'command', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Project.project_name'
        db.alter_column(u'projects_project', 'project_name', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Project.name'
        db.alter_column(u'projects_project', 'name', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Project.queue'
        db.alter_column(u'projects_project', 'queue', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'ScheduledCommand.command'
        db.alter_column(u'projects_scheduledcommand', 'command', self.gf('django.db.models.fields.CharField')(max_length=256))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'projects.commandlog': {
            'Meta': {'object_name': 'CommandLog'},
            'command': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.files.FileField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'return_code': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'projects.project': {
            'Meta': {'object_name': 'Project'},
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'queue': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'projects.scheduledcommand': {
            'Meta': {'object_name': 'ScheduledCommand'},
            'command': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval_minutes': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'last_run': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'projects.shoveinstance': {
            'Meta': {'object_name': 'ShoveInstance'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_heartbeat': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'routing_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['projects']