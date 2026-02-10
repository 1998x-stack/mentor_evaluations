/**
 * Radar Chart Component
 * Pure JavaScript implementation without external dependencies
 */

class RadarChart {
    constructor(canvas, options = {}) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Default options
        this.options = {
            radius: 120,
            levels: 5,
            maxValue: 10,
            labelFont: '14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
            valueFont: 'bold 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
            strokeColor: '#d2d2d7',
            fillColor: 'rgba(102, 126, 234, 0.2)',
            lineColor: 'rgba(102, 126, 234, 1)',
            pointColor: '#667eea',
            labelColor: '#1d1d1f',
            gridColor: '#f5f5f7',
            ...options
        };

        this.data = [];
        this.labels = [];

        this.setupCanvas();
    }

    setupCanvas() {
        // Set canvas size for high DPI displays
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();

        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;

        this.ctx.scale(dpr, dpr);

        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';

        this.centerX = rect.width / 2;
        this.centerY = rect.height / 2;
    }

    setData(labels, values) {
        this.labels = labels;
        this.data = values;
        this.draw();
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.drawGrid();
        this.drawData();
        this.drawLabels();
    }

    drawGrid() {
        const { levels, radius, strokeColor, gridColor } = this.options;
        const angleStep = (Math.PI * 2) / this.labels.length;

        // Draw concentric polygons
        for (let level = 1; level <= levels; level++) {
            const r = (radius / levels) * level;

            this.ctx.beginPath();
            this.ctx.strokeStyle = level === levels ? strokeColor : gridColor;
            this.ctx.lineWidth = level === levels ? 2 : 1;

            for (let i = 0; i <= this.labels.length; i++) {
                const angle = angleStep * i - Math.PI / 2;
                const x = this.centerX + r * Math.cos(angle);
                const y = this.centerY + r * Math.sin(angle);

                if (i === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    this.ctx.lineTo(x, y);
                }
            }

            this.ctx.closePath();
            this.ctx.stroke();
        }

        // Draw lines from center to vertices
        this.ctx.strokeStyle = gridColor;
        this.ctx.lineWidth = 1;

        for (let i = 0; i < this.labels.length; i++) {
            const angle = angleStep * i - Math.PI / 2;
            const x = this.centerX + radius * Math.cos(angle);
            const y = this.centerY + radius * Math.sin(angle);

            this.ctx.beginPath();
            this.ctx.moveTo(this.centerX, this.centerY);
            this.ctx.lineTo(x, y);
            this.ctx.stroke();
        }
    }

    drawData() {
        const { radius, maxValue, fillColor, lineColor, pointColor } = this.options;
        const angleStep = (Math.PI * 2) / this.labels.length;

        // Draw filled area
        this.ctx.beginPath();
        this.ctx.fillStyle = fillColor;

        for (let i = 0; i < this.data.length; i++) {
            const value = this.data[i];
            const r = (radius * value) / maxValue;
            const angle = angleStep * i - Math.PI / 2;
            const x = this.centerX + r * Math.cos(angle);
            const y = this.centerY + r * Math.sin(angle);

            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }

        this.ctx.closePath();
        this.ctx.fill();

        // Draw line
        this.ctx.beginPath();
        this.ctx.strokeStyle = lineColor;
        this.ctx.lineWidth = 2.5;

        for (let i = 0; i < this.data.length; i++) {
            const value = this.data[i];
            const r = (radius * value) / maxValue;
            const angle = angleStep * i - Math.PI / 2;
            const x = this.centerX + r * Math.cos(angle);
            const y = this.centerY + r * Math.sin(angle);

            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }

        this.ctx.closePath();
        this.ctx.stroke();

        // Draw points
        for (let i = 0; i < this.data.length; i++) {
            const value = this.data[i];
            const r = (radius * value) / maxValue;
            const angle = angleStep * i - Math.PI / 2;
            const x = this.centerX + r * Math.cos(angle);
            const y = this.centerY + r * Math.sin(angle);

            this.ctx.beginPath();
            this.ctx.fillStyle = pointColor;
            this.ctx.arc(x, y, 5, 0, Math.PI * 2);
            this.ctx.fill();

            // White border
            this.ctx.beginPath();
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.arc(x, y, 5, 0, Math.PI * 2);
            this.ctx.stroke();
        }
    }

    drawLabels() {
        const { radius, labelFont, valueFont, labelColor } = this.options;
        const angleStep = (Math.PI * 2) / this.labels.length;
        const labelOffset = 30;

        this.ctx.fillStyle = labelColor;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        for (let i = 0; i < this.labels.length; i++) {
            const angle = angleStep * i - Math.PI / 2;
            const labelX = this.centerX + (radius + labelOffset) * Math.cos(angle);
            const labelY = this.centerY + (radius + labelOffset) * Math.sin(angle);

            // Draw label
            this.ctx.font = labelFont;
            this.ctx.fillText(this.labels[i], labelX, labelY);

            // Draw value
            if (this.data[i] !== undefined) {
                this.ctx.font = valueFont;
                this.ctx.fillText(
                    this.data[i].toFixed(1),
                    labelX,
                    labelY + 18
                );
            }
        }
    }

    resize() {
        this.setupCanvas();
        if (this.data.length > 0) {
            this.draw();
        }
    }
}

// Auto-resize on window resize
window.addEventListener('resize', () => {
    const charts = document.querySelectorAll('canvas[data-radar-chart]');
    charts.forEach(canvas => {
        if (canvas.radarChart) {
            canvas.radarChart.resize();
        }
    });
});
