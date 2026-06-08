{{- define "web14-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "web14-app.labels" -}}
helm.sh/chart: {{ include "web14-app.name" . }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
org.bstu.student.fullname: {{ .Values.student.fullname }}
org.bstu.student.id: {{ .Values.student.id }}
org.bstu.group: {{ .Values.student.group }}
org.bstu.variant: {{ .Values.student.variant }}
org.bstu.course: RSIOT
org.bstu.owner: {{ .Values.student.owner }}
org.bstu.student.slug: {{ .Values.student.slug }}
{{- end }}