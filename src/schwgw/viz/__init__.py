"""Visualization helpers for saved results."""

from schwgw.viz.fig4_comparison import (
    Fig4ComparisonError,
    asymptotic_total_polarizations,
    render_fig4_exact_asymptotic_comparison,
)
from schwgw.viz.tablei_review_grid import (
    ReviewGridPlotError,
    plot_tablei_review_grid_diagnostics,
)
from schwgw.viz.tablei_uniform import UniformFigureError, render_tablei_uniform_figures
from schwgw.viz.fig7_apparent import (
    Fig7ApparentArtifacts,
    Fig7ApparentPlotError,
    render_fig7_apparent_four_frequency,
)
from schwgw.viz.fig8_asymptotic import (
    Fig8AsymptoticArtifacts,
    Fig8AsymptoticPlotError,
    render_fig8_asymptotic_four_frequency,
)
from schwgw.viz.results import (
    PlotError,
    plot_amplification_from_result,
    plot_convergence_from_result,
    plot_fig3_multifrequency_panel_from_results,
    plot_fig3_panel_from_result,
    plot_fig4_all_frequency_exact_angular_from_results,
    plot_fig4_exact_angular_from_result,
    plot_tablei_four_frequency_report,
    plot_wavefield_from_result,
)

__all__ = [
    "PlotError",
    "Fig4ComparisonError",
    "Fig7ApparentArtifacts",
    "Fig7ApparentPlotError",
    "Fig8AsymptoticArtifacts",
    "Fig8AsymptoticPlotError",
    "ReviewGridPlotError",
    "asymptotic_total_polarizations",
    "plot_amplification_from_result",
    "plot_convergence_from_result",
    "plot_fig3_multifrequency_panel_from_results",
    "plot_fig3_panel_from_result",
    "plot_fig4_all_frequency_exact_angular_from_results",
    "plot_fig4_exact_angular_from_result",
    "render_fig7_apparent_four_frequency",
    "render_fig8_asymptotic_four_frequency",
    "render_fig4_exact_asymptotic_comparison",
    "plot_tablei_four_frequency_report",
    "plot_tablei_review_grid_diagnostics",
    "plot_wavefield_from_result",
    "UniformFigureError",
    "render_tablei_uniform_figures",
]
