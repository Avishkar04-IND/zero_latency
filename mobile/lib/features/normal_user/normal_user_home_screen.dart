import 'package:flutter/material.dart';

class NormalUserHomeScreen extends StatelessWidget {
  const NormalUserHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Medicine — Standard Mode'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: const [
              Icon(Icons.medical_services_outlined, size: 64, color: Colors.blue),
              SizedBox(height: 16),
              Text(
                'Standard Mobile UI',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text(
                'This module is independently developed by the Normal User Mobile Teammate.',
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
