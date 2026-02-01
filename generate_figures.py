#!/usr/bin/env python3
"""Generate all paper figures from extracted data."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), 'latex', 'figures')
os.makedirs(OUT_DIR, exist_ok=True)

# Updated data from production (Feb 2026 extraction)
vectors = [
    'completion', 'change', 'state', 'know', 'context', 'do',
    'clarity', 'density', 'signal', 'coherence', 'impact', 'engagement', 'uncertainty'
]
evidence = [203, 179, 174, 267, 251, 178, 192, 172, 172, 178, 188, 228, 263]
prior = [0.204, 0.516, 0.645, 0.663, 0.705, 0.693, 0.734, 0.591, 0.703, 0.747, 0.704, 0.860, 0.363]
posterior = [0.909, 0.754, 0.851, 0.863, 0.860, 0.843, 0.879, 0.732, 0.839, 0.874, 0.826, 0.882, 0.154]
delta = [p - q for p, q in zip(posterior, prior)]

# Convergence data
conv_evidence = ['1-5', '6-15', '16-40', '41-87', '88-175', '176+']
conv_beliefs = [399, 390, 567, 618, 1180, 1043]
conv_variance = [0.0477, 0.0099, 0.0042, 0.0016, 0.0008, 0.0004]
conv_reduction = [1, 5, 11, 30, 60, 115]

# Grounded calibration gap data
grounded_vectors = ['do', 'completion', 'uncertainty', 'context', 'know', 'signal']
grounded_self = [0.885, 0.625, 0.134, 0.850, 0.866, 0.774]
grounded_evidence = [0.500, 0.500, 0.091, 0.867, 0.900, 1.000]
grounded_gap = [0.385, 0.125, 0.043, -0.017, -0.034, -0.226]

plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    'capability': '#2196F3',
    'uncertainty': '#FF5722',
    'engagement': '#4CAF50',
    'prior': '#90CAF9',
    'posterior': '#1565C0',
    'grounded': '#9C27B0',
    'overest': '#FF5722',
    'underest': '#2196F3',
    'neutral': '#9E9E9E',
}


def fig1_unified_confidence():
    """All 13 vectors showing unified confidence growth."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Convert uncertainty to confidence scale for unified view
    conf_prior = prior.copy()
    conf_posterior = posterior.copy()
    conf_prior[-1] = 1 - conf_prior[-1]  # uncertainty inverted
    conf_posterior[-1] = 1 - conf_posterior[-1]

    x = np.arange(len(vectors))
    width = 0.35

    colors_prior = [COLORS['prior']] * 12 + [COLORS['prior']]
    colors_post = [COLORS['posterior']] * 12 + [COLORS['posterior']]

    bars1 = ax.bar(x - width/2, conf_prior, width, label='PREFLIGHT',
                   color=colors_prior, edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, conf_posterior, width, label='POSTFLIGHT',
                   color=colors_post, edgecolor='white', linewidth=0.5)

    # Mark uncertainty as inverted
    ax.annotate('(inverted)', xy=(12, conf_prior[-1]), fontsize=7,
                ha='center', va='bottom', color='gray')

    ax.set_xlabel('Epistemic Vector', fontsize=11)
    ax.set_ylabel('Confidence (0-1)', fontsize=11)
    ax.set_title('Unified Confidence Growth Across All 13 Epistemic Vectors', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([v.upper() for v in vectors], rotation=45, ha='right', fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=10)

    # Add delta annotations
    for i in range(len(vectors)):
        d = conf_posterior[i] - conf_prior[i]
        ax.annotate(f'+{d:.2f}', xy=(x[i] + width/2, conf_posterior[i]),
                    fontsize=6.5, ha='center', va='bottom', color='#1B5E20')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'fig1_unified_confidence.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  fig1_unified_confidence.png')


def fig2_evidence_distribution():
    """Evidence distribution across vectors."""
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(vectors))
    colors = [COLORS['capability']] * 12 + [COLORS['uncertainty']]

    bars = ax.bar(x, evidence, color=colors, edgecolor='white', linewidth=0.5)

    ax.set_xlabel('Epistemic Vector', fontsize=11)
    ax.set_ylabel('Evidence Count', fontsize=11)
    ax.set_title('Evidence Distribution Across Epistemic Vectors', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([v.upper() for v in vectors], rotation=45, ha='right', fontsize=9)

    # Add count labels
    for bar, count in zip(bars, evidence):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                str(count), ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'fig2_evidence_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  fig2_evidence_distribution.png')


def fig3_learning_delta():
    """Learning delta: prior vs posterior per vector."""
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(vectors))
    width = 0.35

    ax.bar(x - width/2, prior, width, label='PREFLIGHT (Prior)',
           color=COLORS['prior'], edgecolor='white', linewidth=0.5)
    ax.bar(x + width/2, posterior, width, label='POSTFLIGHT (Posterior)',
           color=COLORS['posterior'], edgecolor='white', linewidth=0.5)

    # Add delta annotations
    for i in range(len(vectors)):
        d = delta[i]
        sign = '+' if d >= 0 else ''
        color = '#1B5E20' if d >= 0 else '#B71C1C'
        midpoint = (prior[i] + posterior[i]) / 2
        ax.annotate(f'{sign}{d:.3f}', xy=(x[i], max(prior[i], posterior[i]) + 0.02),
                    fontsize=7, ha='center', va='bottom', color=color, fontweight='bold')

    ax.set_xlabel('Epistemic Vector', fontsize=11)
    ax.set_ylabel('Assessment Value (0-1)', fontsize=11)
    ax.set_title('Learning Delta: PREFLIGHT vs POSTFLIGHT Assessment', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([v.upper() for v in vectors], rotation=45, ha='right', fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'fig3_learning_delta.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  fig3_learning_delta.png')


def fig4_reframing():
    """Reframing: raw deltas vs confidence-aligned deltas."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Raw deltas
    colors_raw = [COLORS['capability'] if d >= 0 else COLORS['uncertainty'] for d in delta]
    ax1.barh(range(len(vectors)), delta, color=colors_raw, edgecolor='white', linewidth=0.5)
    ax1.set_yticks(range(len(vectors)))
    ax1.set_yticklabels([v.upper() for v in vectors], fontsize=9)
    ax1.set_xlabel('Raw Delta', fontsize=10)
    ax1.set_title('Raw Deltas (Apparent 12:1 Asymmetry)', fontsize=11, fontweight='bold')
    ax1.axvline(x=0, color='black', linewidth=0.5)

    # Right: Confidence-aligned (invert uncertainty)
    conf_delta = delta.copy()
    conf_delta[-1] = -conf_delta[-1]  # Invert uncertainty
    colors_conf = [COLORS['capability']] * len(vectors)
    ax2.barh(range(len(vectors)), conf_delta, color=colors_conf, edgecolor='white', linewidth=0.5)
    ax2.set_yticks(range(len(vectors)))
    ax2.set_yticklabels([v.upper() for v in vectors], fontsize=9)
    ax2.set_xlabel('Confidence Delta', fontsize=10)
    ax2.set_title('Unified Confidence Growth (All 13 Positive)', fontsize=11, fontweight='bold')
    ax2.axvline(x=0, color='black', linewidth=0.5)

    # Label the inverted uncertainty
    ax2.annotate('uncertainty\n(inverted)', xy=(conf_delta[-1], 12),
                 fontsize=7, ha='left', va='center', color='gray',
                 xytext=(conf_delta[-1] + 0.05, 12))

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'fig4_reframing.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  fig4_reframing.png')


def fig5_calibration_convergence():
    """Calibration convergence: variance vs evidence."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    x = range(len(conv_evidence))

    # Left: Variance
    ax1.bar(x, conv_variance, color=COLORS['capability'], edgecolor='white', linewidth=0.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(conv_evidence, fontsize=9)
    ax1.set_xlabel('Evidence Count', fontsize=10)
    ax1.set_ylabel('Average Variance', fontsize=10)
    ax1.set_title('Calibration Variance by Evidence Level', fontsize=11, fontweight='bold')
    for i, v in enumerate(conv_variance):
        ax1.text(i, v + 0.001, f'{v:.4f}', ha='center', va='bottom', fontsize=8)

    # Right: Reduction factor
    ax2.bar(x, conv_reduction, color=COLORS['posterior'], edgecolor='white', linewidth=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(conv_evidence, fontsize=9)
    ax2.set_xlabel('Evidence Count', fontsize=10)
    ax2.set_ylabel('Variance Reduction Factor', fontsize=10)
    ax2.set_title('Calibration Convergence', fontsize=11, fontweight='bold')
    for i, r in enumerate(conv_reduction):
        ax2.text(i, r + 1, f'{r}x', ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'fig5_calibration_convergence.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  fig5_calibration_convergence.png')


def fig6_grounded_calibration_gap():
    """NEW: Grounded calibration gap visualization."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(grounded_vectors))
    width = 0.35

    # Self-assessed vs evidence-grounded bars
    ax.bar(x - width/2, grounded_self, width, label='Self-Assessed (POSTFLIGHT)',
           color=COLORS['capability'], edgecolor='white', linewidth=0.5)
    ax.bar(x + width/2, grounded_evidence, width, label='Evidence-Grounded (POST-TEST)',
           color=COLORS['grounded'], edgecolor='white', linewidth=0.5)

    # Add gap annotations
    for i, gap in enumerate(grounded_gap):
        sign = '+' if gap >= 0 else ''
        color = COLORS['overest'] if gap > 0.05 else (COLORS['underest'] if gap < -0.05 else COLORS['neutral'])
        y_pos = max(grounded_self[i], grounded_evidence[i]) + 0.03
        label = 'overest.' if gap > 0.05 else ('underest.' if gap < -0.05 else 'calibrated')
        ax.annotate(f'gap: {sign}{gap:.3f}\n({label})',
                    xy=(x[i], y_pos), fontsize=8, ha='center', va='bottom',
                    color=color, fontweight='bold')

    ax.set_xlabel('Epistemic Vector', fontsize=11)
    ax.set_ylabel('Assessment Value (0-1)', fontsize=11)
    ax.set_title('Grounded Calibration Gap: Self-Assessed vs Evidence-Derived\n(N=7 verifications, 25 evidence observations)',
                 fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([v.upper() for v in grounded_vectors], fontsize=10)
    ax.set_ylim(0, 1.25)
    ax.legend(fontsize=10, loc='upper right')

    # Add horizontal line at 0 gap reference
    ax.axhline(y=0, color='gray', linewidth=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'fig6_grounded_calibration_gap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print('  fig6_grounded_calibration_gap.png')


if __name__ == '__main__':
    print('Generating paper figures...')
    fig1_unified_confidence()
    fig2_evidence_distribution()
    fig3_learning_delta()
    fig4_reframing()
    fig5_calibration_convergence()
    fig6_grounded_calibration_gap()
    print('Done. All figures in', OUT_DIR)
