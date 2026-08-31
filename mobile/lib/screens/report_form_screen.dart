import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../models/report.dart';
import '../services/api_client.dart';
import '../services/location_service.dart';
import '../services/offline_queue.dart';
import '../theme.dart';

/// Pantalla principal del ciudadano: capturar el punto crítico en menos de un
/// minuto. El flujo es foto -> categoría -> severidad -> enviar; la ubicación
/// se resuelve en segundo plano mientras el usuario completa el formulario.
class ReportFormScreen extends StatefulWidget {
  const ReportFormScreen({
    super.key,
    required this.api,
    required this.location,
    required this.queue,
  });

  final ApiClient api;
  final LocationService location;
  final OfflineQueue queue;

  @override
  State<ReportFormScreen> createState() => _ReportFormScreenState();
}

class _ReportFormScreenState extends State<ReportFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _description = TextEditingController();

  WasteCategory _category = WasteCategory.escombros;
  double _severity = 3;
  File? _photo;
  bool _sending = false;

  @override
  void dispose() {
    _description.dispose();
    super.dispose();
  }

  Future<void> _takePhoto() async {
    final picked = await ImagePicker().pickImage(
      source: ImageSource.camera,
      maxWidth: 1600,
      imageQuality: 80, // comprime en el dispositivo: menos datos móviles
    );
    if (picked != null) setState(() => _photo = File(picked.path));
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _sending = true);

    try {
      final position = await widget.location.current();

      String? evidenceKey;
      if (_photo != null) {
        evidenceKey = await widget.api.uploadEvidence(_photo!, 'image/jpeg');
      }

      final report = Report(
        reportId: '',
        lat: position.latitude,
        lon: position.longitude,
        category: _category,
        severity: _severity.round(),
        status: ReportStatus.reportado,
        createdAt: DateTime.now(),
        description: _description.text.trim(),
        evidenceKey: evidenceKey,
      );

      try {
        await widget.api.createReport(report);
        _notify('Reporte enviado. Gracias por cuidar tu barrio.');
      } on ApiException catch (e) {
        if (e.statusCode == 0 || e.statusCode >= 500) {
          await widget.queue.enqueue(report);
          _notify('Sin conexión: el reporte se enviará automáticamente.');
        } else {
          rethrow;
        }
      }
      if (mounted) _reset();
    } on LocationDeniedException catch (e) {
      _notify(e.message, error: true);
    } on ApiException catch (e) {
      _notify(e.message, error: true);
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  void _reset() {
    _description.clear();
    setState(() {
      _photo = null;
      _severity = 3;
      _category = WasteCategory.escombros;
    });
  }

  void _notify(String message, {bool error = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: error ? Theme.of(context).colorScheme.error : null,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Nuevo reporte')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _PhotoPicker(photo: _photo, onTap: _takePhoto),
            const SizedBox(height: 20),
            DropdownButtonFormField<WasteCategory>(
              value: _category,
              decoration: const InputDecoration(labelText: 'Tipo de residuo'),
              items: WasteCategory.values
                  .where((c) => c != WasteCategory.noClasificado)
                  .map((c) => DropdownMenuItem(value: c, child: Text(c.label)))
                  .toList(),
              onChanged: (v) => setState(() => _category = v ?? _category),
            ),
            const SizedBox(height: 20),
            Text(
              'Severidad: ${_severity.round()}',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            Slider(
              value: _severity,
              min: 1,
              max: 5,
              divisions: 4,
              label: '${_severity.round()}',
              activeColor: EcoTheme.severityColor(_severity.round(), scheme),
              onChanged: (v) => setState(() => _severity = v),
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: _description,
              maxLines: 3,
              maxLength: 500,
              decoration: const InputDecoration(
                labelText: 'Descripción (opcional)',
                hintText: 'Ej.: acumulación en el andén frente al parque',
              ),
            ),
            const SizedBox(height: 8),
            FilledButton.icon(
              onPressed: _sending ? null : _submit,
              icon: _sending
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.send),
              label: Text(_sending ? 'Enviando…' : 'Enviar reporte'),
            ),
          ],
        ),
      ),
    );
  }
}

class _PhotoPicker extends StatelessWidget {
  const _PhotoPicker({required this.photo, required this.onTap});

  final File? photo;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Semantics(
        button: true,
        label: photo == null ? 'Tomar fotografía de la evidencia' : 'Cambiar fotografía',
        child: Container(
          height: 200,
          decoration: BoxDecoration(
            color: scheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: scheme.outlineVariant),
            image: photo != null
                ? DecorationImage(image: FileImage(photo!), fit: BoxFit.cover)
                : null,
          ),
          child: photo != null
              ? null
              : Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.add_a_photo_outlined, size: 40, color: scheme.primary),
                    const SizedBox(height: 8),
                    const Text('Tomar foto de la evidencia'),
                  ],
                ),
        ),
      ),
    );
  }
}
