import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available for PDF generation")

logger = logging.getLogger(__name__)

class ReportService:
    """Service for generating medical reports in PDF and JSON formats."""
    
    def __init__(self):
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self._initialize_styles()
    
    def _initialize_styles(self):
        """Initialize ReportLab styles for PDF generation."""
        self.styles = getSampleStyleSheet()
        
        # Custom styles for medical reports
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkgreen
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='ImportantText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))
    
    async def generate_pdf_report(self, report_context: Dict[str, Any], output_path: str):
        """
        Generate a comprehensive PDF medical report.
        
        Args:
            report_context: Report data and context
            output_path: Path to save the PDF file
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab not available, cannot generate PDF")
            return
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build report content
            story = []
            
            # Header
            story.extend(self._build_report_header(report_context))
            
            # Patient Information
            story.extend(self._build_patient_section(report_context))
            
            # Analysis Results
            story.extend(self._build_analysis_sections(report_context))
            
            # Summary and Recommendations
            story.extend(self._build_summary_section(report_context))
            
            # Footer
            story.extend(self._build_report_footer(report_context))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _build_report_header(self, context: Dict[str, Any]) -> List:
        """Build report header section."""
        story = []
        
        # Title
        title = "MedAI Copilot - Medical Analysis Report"
        story.append(Paragraph(title, self.styles['ReportTitle']))
        story.append(Spacer(1, 20))
        
        # Report metadata
        metadata_data = [
            ['Report ID:', context['report_id']],
            ['Generated:', context['generated_at'].strftime('%Y-%m-%d %H:%M:%S UTC')],
            ['Report Type:', context['report_type'].title()],
            ['Language:', context['language'].value.upper()],
            ['Analyses Included:', str(len(context['analysis_data']))]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 30))
        
        return story
    
    def _build_patient_section(self, context: Dict[str, Any]) -> List:
        """Build patient information section."""
        story = []
        user = context['user']
        
        story.append(Paragraph("Patient Information", self.styles['SectionHeader']))
        
        patient_data = [
            ['Name:', user.get('full_name', 'N/A')],
            ['Role:', user.get('role', 'N/A').title()],
            ['Language Preference:', user.get('preferred_language', 'en').upper()]
        ]
        
        if user.get('medical_license'):
            patient_data.append(['Medical License:', user['medical_license']])
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_analysis_sections(self, context: Dict[str, Any]) -> List:
        """Build analysis results sections."""
        story = []
        
        story.append(Paragraph("Analysis Results", self.styles['SectionHeader']))
        
        for i, analysis in enumerate(context['analysis_data'], 1):
            analysis_type = analysis.get('analysis_type', 'unknown')
            result = analysis.get('result', {})
            
            # Analysis header
            story.append(Paragraph(
                f"Analysis {i}: {analysis_type.replace('_', ' ').title()}", 
                self.styles['SubHeader']
            ))
            
            # Build specific analysis section
            if analysis_type == 'skin':
                story.extend(self._build_skin_analysis_section(result))
            elif analysis_type == 'radiology':
                story.extend(self._build_radiology_analysis_section(result))
            elif analysis_type == 'triage':
                story.extend(self._build_triage_analysis_section(result))
            
            story.append(Spacer(1, 15))
        
        return story
    
    def _build_skin_analysis_section(self, result: Dict[str, Any]) -> List:
        """Build skin analysis section."""
        story = []
        
        # Top prediction
        story.append(Paragraph(
            f"<b>Primary Finding:</b> {result.get('top_prediction', 'N/A')}", 
            self.styles['BodyText']
        ))
        story.append(Paragraph(
            f"<b>Confidence:</b> {result.get('confidence', 0):.1%}", 
            self.styles['BodyText']
        ))
        story.append(Paragraph(
            f"<b>Risk Level:</b> {result.get('risk_level', 'N/A').title()}", 
            self.styles['BodyText']
        ))
        
        # Predictions table
        predictions = result.get('predictions', {})
        if predictions:
            story.append(Paragraph("Detailed Predictions:", self.styles['SubHeader']))
            
            pred_data = [['Condition', 'Probability']]
            for condition, prob in sorted(predictions.items(), key=lambda x: x[1], reverse=True):
                pred_data.append([condition, f"{prob:.1%}"])
            
            pred_table = Table(pred_data, colWidths=[3*inch, 1.5*inch])
            pred_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(pred_table)
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Recommendations:", self.styles['SubHeader']))
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", self.styles['BodyText']))
        
        return story
    
    def _build_radiology_analysis_section(self, result: Dict[str, Any]) -> List:
        """Build radiology analysis section."""
        story = []
        
        # Scan type and assessment
        story.append(Paragraph(
            f"<b>Scan Type:</b> {result.get('scan_type', 'N/A').replace('_', ' ').title()}", 
            self.styles['BodyText']
        ))
        story.append(Paragraph(
            f"<b>Urgency Level:</b> {result.get('urgency_level', 'N/A').title()}", 
            self.styles['BodyText']
        ))
        
        # Overall assessment
        assessment = result.get('overall_assessment', '')
        if assessment:
            story.append(Paragraph("Overall Assessment:", self.styles['SubHeader']))
            story.append(Paragraph(assessment, self.styles['BodyText']))
        
        # Findings
        findings = result.get('findings', [])
        if findings:
            story.append(Paragraph("Findings:", self.styles['SubHeader']))
            
            findings_data = [['Condition', 'Probability', 'Severity', 'Description']]
            for finding in findings:
                findings_data.append([
                    finding.get('condition', 'N/A'),
                    f"{finding.get('probability', 0):.1%}",
                    finding.get('severity', 'N/A').title(),
                    finding.get('description', 'N/A')[:50] + '...' if len(finding.get('description', '')) > 50 else finding.get('description', 'N/A')
                ])
            
            findings_table = Table(findings_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2.5*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(findings_table)
        
        # Clinical summary
        clinical_summary = result.get('clinical_summary', '')
        if clinical_summary:
            story.append(Paragraph("Clinical Summary:", self.styles['SubHeader']))
            story.append(Paragraph(clinical_summary, self.styles['BodyText']))
        
        return story
    
    def _build_triage_analysis_section(self, result: Dict[str, Any]) -> List:
        """Build triage analysis section."""
        story = []
        
        # Urgency and confidence
        story.append(Paragraph(
            f"<b>Urgency Level:</b> {result.get('urgency_level', 'N/A').title()}", 
            self.styles['BodyText']
        ))
        story.append(Paragraph(
            f"<b>Confidence:</b> {result.get('confidence', 0):.1%}", 
            self.styles['BodyText']
        ))
        story.append(Paragraph(
            f"<b>Care Level:</b> {result.get('care_level', 'N/A')}", 
            self.styles['BodyText']
        ))
        
        # Possible conditions
        conditions = result.get('possible_conditions', [])
        if conditions:
            story.append(Paragraph("Possible Conditions:", self.styles['SubHeader']))
            
            for condition in conditions:
                story.append(Paragraph(
                    f"• <b>{condition.get('name', 'N/A')}</b> ({condition.get('probability', 0):.1%})", 
                    self.styles['BodyText']
                ))
                if condition.get('description'):
                    story.append(Paragraph(
                        f"  {condition['description']}", 
                        self.styles['BodyText']
                    ))
        
        # Red flags
        red_flags = result.get('red_flags', [])
        if red_flags:
            story.append(Paragraph("Warning Signs:", self.styles['SubHeader']))
            for flag in red_flags:
                story.append(Paragraph(f"⚠ {flag}", self.styles['ImportantText']))
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Recommendations:", self.styles['SubHeader']))
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", self.styles['BodyText']))
        
        return story
    
    def _build_summary_section(self, context: Dict[str, Any]) -> List:
        """Build summary and recommendations section."""
        story = []
        
        story.append(Paragraph("Summary and Recommendations", self.styles['SectionHeader']))
        
        # Doctor notes if provided
        doctor_notes = context.get('doctor_notes')
        if doctor_notes:
            story.append(Paragraph("Doctor's Notes:", self.styles['SubHeader']))
            story.append(Paragraph(doctor_notes, self.styles['BodyText']))
            story.append(Spacer(1, 10))
        
        # Overall recommendations based on all analyses
        story.append(Paragraph("Overall Assessment:", self.styles['SubHeader']))
        
        # Determine overall urgency
        urgency_levels = []
        for analysis in context['analysis_data']:
            result = analysis.get('result', {})
            if 'urgency_level' in result:
                urgency_levels.append(result['urgency_level'])
            elif 'risk_level' in result:
                # Convert risk to urgency
                risk_to_urgency = {'low': 'routine', 'medium': 'urgent', 'high': 'urgent', 'critical': 'emergency'}
                urgency_levels.append(risk_to_urgency.get(result['risk_level'], 'routine'))
        
        if urgency_levels:
            max_urgency = max(urgency_levels, key=lambda x: {'routine': 1, 'urgent': 2, 'emergency': 3}.get(x, 1))
            story.append(Paragraph(
                f"Overall urgency level: <b>{max_urgency.title()}</b>", 
                self.styles['BodyText']
            ))
        
        # General recommendations
        story.append(Paragraph("General Recommendations:", self.styles['SubHeader']))
        story.append(Paragraph("• Follow up with your healthcare provider as recommended", self.styles['BodyText']))
        story.append(Paragraph("• Keep this report for your medical records", self.styles['BodyText']))
        story.append(Paragraph("• Seek immediate medical attention if symptoms worsen", self.styles['BodyText']))
        
        return story
    
    def _build_report_footer(self, context: Dict[str, Any]) -> List:
        """Build report footer."""
        story = []
        
        story.append(Spacer(1, 30))
        
        # Disclaimer
        disclaimer = """
        <b>MEDICAL DISCLAIMER:</b> This report is generated by AI-powered analysis tools and is intended 
        for informational purposes only. It should not replace professional medical advice, diagnosis, 
        or treatment. Always consult with qualified healthcare professionals for medical concerns. 
        In case of medical emergencies, call emergency services immediately.
        """
        
        story.append(Paragraph(disclaimer, self.styles['ImportantText']))
        
        # Footer info
        footer_info = f"""
        Generated by MedAI Copilot v2.0<br/>
        Report ID: {context['report_id']}<br/>
        Generated: {context['generated_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        story.append(Spacer(1, 20))
        story.append(Paragraph(footer_info, self.styles['BodyText']))
        
        return story
    
    async def generate_json_report(self, report_context: Dict[str, Any], output_path: str):
        """
        Generate a JSON format medical report.
        
        Args:
            report_context: Report data and context
            output_path: Path to save the JSON file
        """
        try:
            # Prepare JSON report structure
            json_report = {
                "report_metadata": {
                    "report_id": report_context['report_id'],
                    "generated_at": report_context['generated_at'].isoformat(),
                    "report_type": report_context['report_type'],
                    "language": report_context['language'].value,
                    "include_images": report_context['include_images'],
                    "version": "2.0"
                },
                "patient_info": {
                    "user_id": report_context['user']['id'],
                    "full_name": report_context['user'].get('full_name'),
                    "role": report_context['user'].get('role'),
                    "preferred_language": report_context['user'].get('preferred_language'),
                    "medical_license": report_context['user'].get('medical_license')
                },
                "analyses": [],
                "summary": {
                    "total_analyses": len(report_context['analysis_data']),
                    "doctor_notes": report_context.get('doctor_notes'),
                    "overall_urgency": self._calculate_overall_urgency(report_context['analysis_data'])
                },
                "disclaimer": "This report is generated by AI-powered analysis tools and should not replace professional medical advice."
            }
            
            # Add analysis results
            for analysis in report_context['analysis_data']:
                analysis_entry = {
                    "analysis_id": analysis['analysis_id'],
                    "analysis_type": analysis['analysis_type'],
                    "timestamp": analysis['timestamp'],
                    "result": analysis['result']
                }
                
                # Add clinical history if available
                if 'clinical_history' in analysis:
                    analysis_entry['clinical_history'] = analysis['clinical_history']
                
                json_report['analyses'].append(analysis_entry)
            
            # Save JSON report
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"JSON report generated: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            raise
    
    def _calculate_overall_urgency(self, analysis_data: List[Dict[str, Any]]) -> str:
        """Calculate overall urgency from all analyses."""
        urgency_levels = []
        
        for analysis in analysis_data:
            result = analysis.get('result', {})
            if 'urgency_level' in result:
                urgency_levels.append(result['urgency_level'])
            elif 'risk_level' in result:
                # Convert risk to urgency
                risk_to_urgency = {
                    'low': 'routine', 
                    'medium': 'urgent', 
                    'high': 'urgent', 
                    'critical': 'emergency'
                }
                urgency_levels.append(risk_to_urgency.get(result['risk_level'], 'routine'))
        
        if not urgency_levels:
            return 'routine'
        
        # Return highest urgency level
        urgency_priority = {'routine': 1, 'urgent': 2, 'emergency': 3}
        max_urgency = max(urgency_levels, key=lambda x: urgency_priority.get(x, 1))
        
        return max_urgency
