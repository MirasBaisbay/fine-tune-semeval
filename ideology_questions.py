"""
Ideology Question Bank for Media Bias Analysis

This module contains structured questions with academic references for evaluating
media sources on Economic and Social dimensions per MBFC methodology.

Methodology:
1. Each question has a yes/no/irrelevant answer format
2. Questions map to specific ideology scores (-10 to +10)
3. All questions have academic references from political science, economics, and sociology
4. Keywords are provided for searching relevant articles

Usage:
1. Search articles using keywords
2. For matching articles, ask LLM: "Does this article support X? Yes/No/Irrelevant"
3. Aggregate answers weighted by relevance to determine final score

References:
- Stanford Encyclopedia of Philosophy: https://plato.stanford.edu/
- Internet Encyclopedia of Philosophy: https://iep.utm.edu/
- Britannica: https://www.britannica.com/
- IMF Finance & Development: https://www.imf.org/external/pubs/ft/fandd/
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class IdeologyType(Enum):
    ECONOMIC = "economic"
    SOCIAL = "social"


@dataclass
class AcademicReference:
    """Academic source reference for a question."""
    author: str
    title: str
    year: int
    source_type: str  # "book", "article", "encyclopedia", "institution"
    url: Optional[str] = None

    def __str__(self):
        return f"{self.author} ({self.year}). {self.title}"


@dataclass
class IdeologyQuestion:
    """A structured question for ideology detection."""
    question: str
    yes_maps_to: str  # Ideology label
    yes_score: float  # Score on -10 to +10 scale
    no_maps_to: Optional[str] = None  # Optional: what "no" answer indicates
    no_score: Optional[float] = None
    keywords: List[str] = field(default_factory=list)
    references: List[AcademicReference] = field(default_factory=list)
    category: str = ""  # Sub-category within economic/social
    weight: float = 1.0  # Relative importance of this question
    notes: str = ""  # Additional context for reviewers


# =============================================================================
# ECONOMIC SYSTEM QUESTIONS (-10 to +10)
# =============================================================================
# Scale: Communism (-10) → Socialism (-7.5) → Democratic Socialism (-5) →
#        Regulated Market (-2.5) → Centrism (0) → Moderate Capitalism (+2.5) →
#        Classical Liberalism (+5) → Libertarianism (+7.5) → Laissez-Faire (+10)
# =============================================================================

ECONOMIC_QUESTIONS: List[IdeologyQuestion] = [

    # =========================================================================
    # COMMUNISM (-10) - Full state ownership, abolition of private property
    # =========================================================================
    IdeologyQuestion(
        question="Does this article advocate for the complete abolition of private property?",
        yes_maps_to="Communism",
        yes_score=-10.0,
        keywords=[
            "abolish private property", "end private ownership", "collective ownership of all",
            "no private property", "property is theft", "communal ownership"
        ],
        references=[
            AcademicReference(
                author="Marx, K. & Engels, F.",
                title="The Communist Manifesto",
                year=1848,
                source_type="book",
                url="https://www.marxists.org/archive/marx/works/1848/communist-manifesto/"
            ),
            AcademicReference(
                author="Stanford Encyclopedia of Philosophy",
                title="Socialism",
                year=2022,
                source_type="encyclopedia",
                url="https://plato.stanford.edu/entries/socialism/"
            )
        ],
        category="property_rights",
        weight=1.0,
        notes="Core tenet of Marxist communism - abolition of bourgeois property relations"
    ),

    IdeologyQuestion(
        question="Does this article call for workers to seize control of all means of production?",
        yes_maps_to="Communism",
        yes_score=-10.0,
        keywords=[
            "seize means of production", "workers control factories", "expropriate capitalists",
            "worker revolution", "proletarian revolution", "class struggle"
        ],
        references=[
            AcademicReference(
                author="Marx, K.",
                title="Das Kapital: Critique of Political Economy",
                year=1867,
                source_type="book"
            ),
            AcademicReference(
                author="Britannica",
                title="Communism",
                year=2024,
                source_type="encyclopedia",
                url="https://www.britannica.com/topic/communism"
            )
        ],
        category="means_of_production",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article advocate for a classless, stateless society as the end goal?",
        yes_maps_to="Communism",
        yes_score=-10.0,
        keywords=[
            "classless society", "stateless society", "wither away of the state",
            "abolish social classes", "end of class distinction", "communist utopia"
        ],
        references=[
            AcademicReference(
                author="Marx, K.",
                title="Critique of the Gotha Programme",
                year=1875,
                source_type="book"
            ),
            AcademicReference(
                author="Lenin, V.I.",
                title="The State and Revolution",
                year=1917,
                source_type="book"
            )
        ],
        category="social_structure",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article support distribution based on 'from each according to ability, to each according to needs'?",
        yes_maps_to="Communism",
        yes_score=-10.0,
        keywords=[
            "from each according to ability", "to each according to needs",
            "communist distribution", "need-based distribution"
        ],
        references=[
            AcademicReference(
                author="Marx, K.",
                title="Critique of the Gotha Programme",
                year=1875,
                source_type="book"
            )
        ],
        category="distribution",
        weight=0.9
    ),

    # =========================================================================
    # SOCIALISM (-7.5) - Significant state ownership, high regulation
    # =========================================================================
    IdeologyQuestion(
        question="Does this article advocate for government ownership of major industries (energy, transportation, healthcare)?",
        yes_maps_to="Socialism",
        yes_score=-7.5,
        keywords=[
            "nationalize industry", "public ownership", "state-owned enterprises",
            "government ownership", "nationalization", "socialize industry"
        ],
        references=[
            AcademicReference(
                author="Harrington, M.",
                title="Socialism: Past and Future",
                year=1989,
                source_type="book"
            ),
            AcademicReference(
                author="Internet Encyclopedia of Philosophy",
                title="Socialism",
                year=2023,
                source_type="encyclopedia",
                url="https://iep.utm.edu/socialis/"
            )
        ],
        category="state_ownership",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support central economic planning over market mechanisms?",
        yes_maps_to="Socialism",
        yes_score=-7.5,
        keywords=[
            "central planning", "planned economy", "economic planning",
            "state allocation", "command economy", "replace market"
        ],
        references=[
            AcademicReference(
                author="Kornai, J.",
                title="The Socialist System: The Political Economy of Communism",
                year=1992,
                source_type="book",
                url="https://academic.oup.com/book/4729"
            )
        ],
        category="market_vs_planning",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article argue that profit motive is inherently exploitative and should be eliminated?",
        yes_maps_to="Socialism",
        yes_score=-7.5,
        keywords=[
            "profit is exploitation", "abolish profit", "end profit motive",
            "exploitation of workers", "surplus value theft", "capitalist exploitation"
        ],
        references=[
            AcademicReference(
                author="Marx, K.",
                title="Das Kapital, Volume I",
                year=1867,
                source_type="book"
            ),
            AcademicReference(
                author="Cohen, G.A.",
                title="Karl Marx's Theory of History: A Defence",
                year=1978,
                source_type="book"
            )
        ],
        category="profit_critique",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article call for worker ownership of their specific workplaces (not just co-determination)?",
        yes_maps_to="Socialism",
        yes_score=-7.5,
        no_maps_to="Democratic Socialism",
        no_score=-5.0,
        keywords=[
            "worker ownership", "worker-owned", "employee ownership",
            "cooperative ownership", "workers own company", "social ownership"
        ],
        references=[
            AcademicReference(
                author="Schweickart, D.",
                title="After Capitalism",
                year=2002,
                source_type="book"
            )
        ],
        category="ownership_structure",
        weight=0.9
    ),

    # =========================================================================
    # DEMOCRATIC SOCIALISM (-5) - Strongly regulated capitalism, extensive welfare
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support universal healthcare as a government-provided right?",
        yes_maps_to="Democratic Socialism",
        yes_score=-5.0,
        keywords=[
            "universal healthcare", "medicare for all", "single-payer",
            "healthcare is a right", "free healthcare", "public health system"
        ],
        references=[
            AcademicReference(
                author="Sanders, B.",
                title="Our Revolution: A Future to Believe In",
                year=2016,
                source_type="book"
            ),
            AcademicReference(
                author="Wikipedia",
                title="Democratic Socialism",
                year=2024,
                source_type="encyclopedia",
                url="https://en.wikipedia.org/wiki/Democratic_socialism"
            )
        ],
        category="welfare_state",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article advocate for free public college/university education?",
        yes_maps_to="Democratic Socialism",
        yes_score=-5.0,
        keywords=[
            "free college", "free university", "tuition-free education",
            "public higher education", "cancel student debt", "education is a right"
        ],
        references=[
            AcademicReference(
                author="Sanders, B.",
                title="Our Revolution: A Future to Believe In",
                year=2016,
                source_type="book"
            )
        ],
        category="education",
        weight=0.7
    ),

    IdeologyQuestion(
        question="Does this article support the Nordic/Scandinavian economic model?",
        yes_maps_to="Democratic Socialism",
        yes_score=-5.0,
        keywords=[
            "nordic model", "scandinavian model", "swedish model",
            "danish model", "norway model", "social democracy"
        ],
        references=[
            AcademicReference(
                author="Esping-Andersen, G.",
                title="The Three Worlds of Welfare Capitalism",
                year=1990,
                source_type="book"
            ),
            AcademicReference(
                author="Nordics.info",
                title="The Nordic Model",
                year=2024,
                source_type="article",
                url="https://nordics.info/themes/the-nordic-model/"
            )
        ],
        category="economic_model",
        weight=1.0,
        notes="Nordic model combines free markets with extensive welfare state"
    ),

    IdeologyQuestion(
        question="Does this article call for significantly higher taxes on the wealthy (e.g., 70%+ top marginal rate)?",
        yes_maps_to="Democratic Socialism",
        yes_score=-5.0,
        keywords=[
            "tax the rich", "wealth tax", "higher taxes wealthy",
            "progressive taxation", "millionaire tax", "billionaire tax",
            "70% tax rate", "90% tax rate"
        ],
        references=[
            AcademicReference(
                author="Piketty, T.",
                title="Capital in the Twenty-First Century",
                year=2014,
                source_type="book"
            )
        ],
        category="taxation",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article support a Green New Deal or similar large-scale government climate intervention?",
        yes_maps_to="Democratic Socialism",
        yes_score=-5.0,
        keywords=[
            "green new deal", "climate jobs program", "government climate investment",
            "public green investment", "climate mobilization"
        ],
        references=[
            AcademicReference(
                author="Ocasio-Cortez, A. & Markey, E.",
                title="Green New Deal Resolution",
                year=2019,
                source_type="article"
            )
        ],
        category="government_intervention",
        weight=0.7
    ),

    # =========================================================================
    # REGULATED MARKET ECONOMY (-2.5) - Moderate regulation, mixed economy
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support Keynesian economics and government stimulus during recessions?",
        yes_maps_to="Regulated Market Economy",
        yes_score=-2.5,
        keywords=[
            "keynesian", "stimulus spending", "government spending recession",
            "fiscal stimulus", "aggregate demand", "counter-cyclical policy"
        ],
        references=[
            AcademicReference(
                author="Keynes, J.M.",
                title="The General Theory of Employment, Interest and Money",
                year=1936,
                source_type="book"
            ),
            AcademicReference(
                author="IMF",
                title="What Is Keynesian Economics?",
                year=2014,
                source_type="article",
                url="https://www.imf.org/external/pubs/ft/fandd/2014/09/basics.htm"
            )
        ],
        category="macroeconomic_policy",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support a mixed economy with both private enterprise and government programs?",
        yes_maps_to="Regulated Market Economy",
        yes_score=-2.5,
        keywords=[
            "mixed economy", "public-private", "government role in economy",
            "market with regulation", "balanced approach economy"
        ],
        references=[
            AcademicReference(
                author="Wikipedia",
                title="Mixed Economy",
                year=2024,
                source_type="encyclopedia",
                url="https://en.wikipedia.org/wiki/Mixed_economy"
            )
        ],
        category="economic_system",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support moderate financial regulations (e.g., Dodd-Frank, consumer protection)?",
        yes_maps_to="Regulated Market Economy",
        yes_score=-2.5,
        keywords=[
            "financial regulation", "bank regulation", "consumer protection",
            "dodd-frank", "wall street reform", "prevent financial crisis"
        ],
        references=[
            AcademicReference(
                author="Stiglitz, J.",
                title="Freefall: America, Free Markets, and the Sinking of the World Economy",
                year=2010,
                source_type="book"
            )
        ],
        category="regulation",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article support maintaining Social Security and Medicare as government programs?",
        yes_maps_to="Regulated Market Economy",
        yes_score=-2.5,
        keywords=[
            "protect social security", "save medicare", "social safety net",
            "maintain entitlements", "strengthen social programs"
        ],
        references=[
            AcademicReference(
                author="Roosevelt, F.D.",
                title="Second Bill of Rights Speech",
                year=1944,
                source_type="article"
            )
        ],
        category="social_programs",
        weight=0.7
    ),

    IdeologyQuestion(
        question="Does this article support antitrust enforcement and breaking up monopolies?",
        yes_maps_to="Regulated Market Economy",
        yes_score=-2.5,
        keywords=[
            "antitrust", "break up monopoly", "competition policy",
            "anti-monopoly", "corporate concentration", "market competition"
        ],
        references=[
            AcademicReference(
                author="Wu, T.",
                title="The Curse of Bigness: Antitrust in the New Gilded Age",
                year=2018,
                source_type="book"
            )
        ],
        category="competition",
        weight=0.8
    ),

    # =========================================================================
    # CENTRISM (0) - Balanced approach, pragmatic
    # =========================================================================
    IdeologyQuestion(
        question="Does this article advocate for pragmatic, case-by-case economic policy without ideological commitment?",
        yes_maps_to="Centrism",
        yes_score=0.0,
        keywords=[
            "pragmatic approach", "bipartisan solution", "middle ground",
            "balanced policy", "evidence-based policy", "technocratic"
        ],
        references=[
            AcademicReference(
                author="Giddens, A.",
                title="The Third Way: The Renewal of Social Democracy",
                year=1998,
                source_type="book"
            )
        ],
        category="ideology",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support both market solutions AND targeted government intervention depending on the issue?",
        yes_maps_to="Centrism",
        yes_score=0.0,
        keywords=[
            "market-based solutions with oversight", "smart regulation",
            "targeted intervention", "balanced approach", "neither extreme"
        ],
        references=[
            AcademicReference(
                author="Blair, T. & Schröder, G.",
                title="Europe: The Third Way/Die Neue Mitte",
                year=1999,
                source_type="article"
            )
        ],
        category="policy_approach",
        weight=0.9
    ),

    # =========================================================================
    # MODERATELY REGULATED CAPITALISM (+2.5) - Market-oriented with some regulation
    # =========================================================================
    IdeologyQuestion(
        question="Does this article argue that markets work well but need modest oversight?",
        yes_maps_to="Moderately Regulated Capitalism",
        yes_score=2.5,
        keywords=[
            "free market with oversight", "light regulation", "market-friendly",
            "pro-business reform", "reduce red tape", "smart deregulation"
        ],
        references=[
            AcademicReference(
                author="Friedman, M.",
                title="Capitalism and Freedom",
                year=1962,
                source_type="book"
            )
        ],
        category="market_regulation",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article support reducing corporate taxes to stimulate growth?",
        yes_maps_to="Moderately Regulated Capitalism",
        yes_score=2.5,
        keywords=[
            "lower corporate tax", "business tax cuts", "corporate tax reform",
            "competitive tax rate", "tax incentives business"
        ],
        references=[
            AcademicReference(
                author="Mankiw, N.G.",
                title="Principles of Economics",
                year=2020,
                source_type="book"
            )
        ],
        category="taxation",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article advocate for free trade with some protections for domestic workers?",
        yes_maps_to="Moderately Regulated Capitalism",
        yes_score=2.5,
        keywords=[
            "free trade agreements", "trade deals", "open markets",
            "trade with protections", "fair trade", "trade adjustment"
        ],
        references=[
            AcademicReference(
                author="Krugman, P.",
                title="Pop Internationalism",
                year=1996,
                source_type="book"
            )
        ],
        category="trade",
        weight=0.7
    ),

    # =========================================================================
    # CLASSICAL LIBERALISM (+5) - Free markets with limited government role
    # =========================================================================
    IdeologyQuestion(
        question="Does this article argue that free markets naturally produce optimal outcomes through the 'invisible hand'?",
        yes_maps_to="Classical Liberalism",
        yes_score=5.0,
        keywords=[
            "invisible hand", "market efficiency", "free market optimal",
            "price mechanism", "spontaneous order", "market self-regulation"
        ],
        references=[
            AcademicReference(
                author="Smith, A.",
                title="The Wealth of Nations",
                year=1776,
                source_type="book"
            ),
            AcademicReference(
                author="Wikipedia",
                title="Classical Liberalism",
                year=2024,
                source_type="encyclopedia",
                url="https://en.wikipedia.org/wiki/Classical_liberalism"
            )
        ],
        category="market_theory",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support significantly reducing government regulations on business?",
        yes_maps_to="Classical Liberalism",
        yes_score=5.0,
        keywords=[
            "deregulation", "reduce regulations", "regulatory burden",
            "government overreach", "free enterprise", "business freedom"
        ],
        references=[
            AcademicReference(
                author="Smith, A.",
                title="The Wealth of Nations",
                year=1776,
                source_type="book"
            ),
            AcademicReference(
                author="Mill, J.S.",
                title="Principles of Political Economy",
                year=1848,
                source_type="book"
            )
        ],
        category="regulation",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article argue that government intervention in markets causes more harm than good?",
        yes_maps_to="Classical Liberalism",
        yes_score=5.0,
        keywords=[
            "government failure", "unintended consequences", "market distortion",
            "government causes problems", "intervention backfires"
        ],
        references=[
            AcademicReference(
                author="Hayek, F.A.",
                title="The Road to Serfdom",
                year=1944,
                source_type="book"
            )
        ],
        category="government_critique",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article support privatization of government services?",
        yes_maps_to="Classical Liberalism",
        yes_score=5.0,
        keywords=[
            "privatization", "privatize", "private sector better",
            "sell state assets", "private efficiency", "outsource government"
        ],
        references=[
            AcademicReference(
                author="Friedman, M.",
                title="Capitalism and Freedom",
                year=1962,
                source_type="book"
            )
        ],
        category="privatization",
        weight=0.8
    ),

    # =========================================================================
    # LIBERTARIANISM (+7.5) - Minimal government, maximum economic freedom
    # =========================================================================
    IdeologyQuestion(
        question="Does this article advocate for abolishing the Federal Reserve or returning to the gold standard?",
        yes_maps_to="Libertarianism",
        yes_score=7.5,
        keywords=[
            "end the fed", "abolish federal reserve", "gold standard",
            "sound money", "audit the fed", "central bank abolition"
        ],
        references=[
            AcademicReference(
                author="Rothbard, M.",
                title="The Case Against the Fed",
                year=1994,
                source_type="book"
            ),
            AcademicReference(
                author="Paul, R.",
                title="End the Fed",
                year=2009,
                source_type="book"
            )
        ],
        category="monetary_policy",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article argue that most government functions should be privatized or eliminated?",
        yes_maps_to="Libertarianism",
        yes_score=7.5,
        keywords=[
            "minimal government", "eliminate departments", "shrink government",
            "night-watchman state", "limited government", "government is the problem"
        ],
        references=[
            AcademicReference(
                author="Nozick, R.",
                title="Anarchy, State, and Utopia",
                year=1974,
                source_type="book"
            ),
            AcademicReference(
                author="Mises, L.",
                title="Human Action: A Treatise on Economics",
                year=1949,
                source_type="book"
            )
        ],
        category="government_size",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support eliminating the minimum wage entirely?",
        yes_maps_to="Libertarianism",
        yes_score=7.5,
        keywords=[
            "abolish minimum wage", "eliminate minimum wage", "no minimum wage",
            "wage should be market-determined", "minimum wage hurts workers"
        ],
        references=[
            AcademicReference(
                author="Rothbard, M.",
                title="Man, Economy, and State",
                year=1962,
                source_type="book"
            )
        ],
        category="labor_policy",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article advocate for abolishing income tax entirely?",
        yes_maps_to="Libertarianism",
        yes_score=7.5,
        keywords=[
            "abolish income tax", "eliminate income tax", "taxation is theft",
            "flat tax", "no income tax", "voluntary taxation"
        ],
        references=[
            AcademicReference(
                author="Rothbard, M.",
                title="For a New Liberty: The Libertarian Manifesto",
                year=1973,
                source_type="book"
            )
        ],
        category="taxation",
        weight=0.9
    ),

    # =========================================================================
    # RADICAL LAISSEZ-FAIRE / ANARCHO-CAPITALISM (+10) - No government role
    # =========================================================================
    IdeologyQuestion(
        question="Does this article argue that ALL government economic functions should be privatized, including courts and police?",
        yes_maps_to="Radical Laissez-Faire",
        yes_score=10.0,
        keywords=[
            "anarcho-capitalism", "private courts", "private police",
            "privatize everything", "voluntary society", "stateless capitalism"
        ],
        references=[
            AcademicReference(
                author="Rothbard, M.",
                title="For a New Liberty: The Libertarian Manifesto",
                year=1973,
                source_type="book"
            ),
            AcademicReference(
                author="Rothbard, M.",
                title="The Ethics of Liberty",
                year=1982,
                source_type="book"
            )
        ],
        category="anarcho_capitalism",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article advocate that taxation is inherently immoral/theft regardless of purpose?",
        yes_maps_to="Radical Laissez-Faire",
        yes_score=10.0,
        keywords=[
            "taxation is theft", "all taxation immoral", "no legitimate taxation",
            "tax is coercion", "involuntary taxation wrong"
        ],
        references=[
            AcademicReference(
                author="Rothbard, M.",
                title="The Ethics of Liberty",
                year=1982,
                source_type="book"
            ),
            AcademicReference(
                author="Nozick, R.",
                title="Anarchy, State, and Utopia",
                year=1974,
                source_type="book"
            )
        ],
        category="taxation_morality",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article argue that the state itself is illegitimate and should be abolished?",
        yes_maps_to="Radical Laissez-Faire",
        yes_score=10.0,
        keywords=[
            "abolish the state", "state is illegitimate", "stateless society",
            "government is evil", "no government needed", "voluntary exchange only"
        ],
        references=[
            AcademicReference(
                author="Rothbard, M.",
                title="For a New Liberty: The Libertarian Manifesto",
                year=1973,
                source_type="book"
            )
        ],
        category="state_legitimacy",
        weight=1.0,
        notes="Note: This is distinct from left-anarchism which also opposes the state"
    ),
]


# =============================================================================
# SOCIAL VALUES QUESTIONS (-10 to +10)
# =============================================================================
# Scale: Strong Progressive (-10) → Progressive (-7.5) → Moderate Progressive (-5) →
#        Mild Progressive (-2.5) → Balanced (0) → Mild Conservative (+2.5) →
#        Moderate Conservative (+5) → Traditional Conservative (+7.5) →
#        Strong Traditional Conservative (+10)
# =============================================================================

SOCIAL_QUESTIONS: List[IdeologyQuestion] = [

    # =========================================================================
    # ABORTION / REPRODUCTIVE RIGHTS
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support unrestricted access to abortion throughout pregnancy?",
        yes_maps_to="Strong Progressive",
        yes_score=-10.0,
        keywords=[
            "abortion on demand", "unrestricted abortion", "abortion any time",
            "no abortion limits", "full reproductive freedom"
        ],
        references=[
            AcademicReference(
                author="Pew Research Center",
                title="Abortion Trends by Party Identification",
                year=2024,
                source_type="article",
                url="https://news.gallup.com/poll/246278/abortion-trends-party.aspx"
            )
        ],
        category="abortion",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support abortion rights with some gestational limits (e.g., first trimester)?",
        yes_maps_to="Progressive",
        yes_score=-7.5,
        keywords=[
            "pro-choice", "reproductive rights", "abortion access",
            "roe v wade", "bodily autonomy", "woman's choice"
        ],
        references=[
            AcademicReference(
                author="Brookings Institution",
                title="Democratic and Republican Parties' positions on reproductive rights",
                year=2024,
                source_type="article",
                url="https://www.brookings.edu/articles/clear-contrasts-between-the-democratic-and-republican-parties-positions-on-reproductive-rights-and-health-care/"
            )
        ],
        category="abortion",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support restricting abortion except in cases of rape, incest, or life of mother?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "abortion restrictions", "limit abortion", "pro-life exceptions",
            "ban most abortions", "protect unborn"
        ],
        references=[
            AcademicReference(
                author="Hout, M. et al.",
                title="Stasis and Sorting of Americans' Abortion Opinions",
                year=2022,
                source_type="article",
                url="https://journals.sagepub.com/doi/full/10.1177/23780231221117648"
            )
        ],
        category="abortion",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support a complete ban on abortion with no exceptions?",
        yes_maps_to="Strong Traditional Conservative",
        yes_score=10.0,
        keywords=[
            "total abortion ban", "ban all abortion", "no abortion ever",
            "life begins at conception", "personhood from conception"
        ],
        references=[
            AcademicReference(
                author="UCSB Imagine Journal",
                title="Race, Religion, and Reproductive Rights",
                year=2025,
                source_type="article",
                url="https://imagine.sa.ucsb.edu/issue/54/2025/race-religion-and-reproductive-rights-understanding-conservative-anti-abortion"
            )
        ],
        category="abortion",
        weight=1.0
    ),

    # =========================================================================
    # LGBTQ+ RIGHTS
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support transgender rights including gender-affirming care for minors?",
        yes_maps_to="Strong Progressive",
        yes_score=-10.0,
        keywords=[
            "trans rights", "gender affirming care", "transgender youth",
            "puberty blockers", "gender identity", "trans healthcare"
        ],
        references=[
            AcademicReference(
                author="University of Oregon",
                title="Republican political strategy and anti-LGBTQ+ rhetoric",
                year=2024,
                source_type="article",
                url="https://socialsciences.uoregon.edu/psasbury-thesis"
            )
        ],
        category="lgbtq",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support same-sex marriage and full LGBTQ+ civil rights?",
        yes_maps_to="Progressive",
        yes_score=-7.5,
        keywords=[
            "marriage equality", "same-sex marriage", "gay rights",
            "lgbtq rights", "anti-discrimination", "equality act"
        ],
        references=[
            AcademicReference(
                author="Pew Research Center",
                title="Same-sex marriage views by party",
                year=2018,
                source_type="article",
                url="https://www.pewresearch.org/politics/2018/03/01/4-race-immigration-same-sex-marriage-abortion-global-warming-gun-policy-marijuana-legalization/"
            )
        ],
        category="lgbtq",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support civil unions but not same-sex marriage?",
        yes_maps_to="Mild Conservative",
        yes_score=2.5,
        keywords=[
            "civil unions", "domestic partnerships", "not marriage",
            "traditional marriage", "compromise on gay rights"
        ],
        references=[
            AcademicReference(
                author="Pew Research Center",
                title="Views on same-sex marriage",
                year=2018,
                source_type="article"
            )
        ],
        category="lgbtq",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article oppose same-sex marriage based on religious or traditional values?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "traditional marriage", "one man one woman", "biblical marriage",
            "marriage is sacred", "oppose gay marriage", "natural marriage"
        ],
        references=[
            AcademicReference(
                author="Wikipedia",
                title="Social conservatism",
                year=2024,
                source_type="encyclopedia",
                url="https://en.wikipedia.org/wiki/Social_conservatism"
            )
        ],
        category="lgbtq",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article characterize LGBTQ+ identity as sinful, disordered, or a threat to society?",
        yes_maps_to="Strong Traditional Conservative",
        yes_score=10.0,
        keywords=[
            "homosexuality is sin", "gay agenda", "lgbtq threat",
            "protect children from lgbt", "grooming", "deviant lifestyle"
        ],
        references=[
            AcademicReference(
                author="Heritage Foundation",
                title="Various publications on LGBTQ issues",
                year=2024,
                source_type="institution"
            )
        ],
        category="lgbtq",
        weight=1.0
    ),

    # =========================================================================
    # IMMIGRATION
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support open borders or dramatically increased immigration?",
        yes_maps_to="Strong Progressive",
        yes_score=-10.0,
        keywords=[
            "open borders", "abolish ice", "no deportations",
            "free movement", "immigration is human right", "borders are violence"
        ],
        references=[
            AcademicReference(
                author="Caplan, B.",
                title="Open Borders: The Science and Ethics of Immigration",
                year=2019,
                source_type="book"
            )
        ],
        category="immigration",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support a pathway to citizenship for undocumented immigrants?",
        yes_maps_to="Progressive",
        yes_score=-7.5,
        keywords=[
            "pathway to citizenship", "dreamers", "daca", "immigration reform",
            "legalize immigrants", "comprehensive immigration reform"
        ],
        references=[
            AcademicReference(
                author="Wikipedia",
                title="Political positions of the Democratic Party",
                year=2024,
                source_type="encyclopedia",
                url="https://en.wikipedia.org/wiki/Political_positions_of_the_Democratic_Party_(United_States)"
            )
        ],
        category="immigration",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support merit-based immigration with border security?",
        yes_maps_to="Mild Conservative",
        yes_score=2.5,
        keywords=[
            "merit-based immigration", "legal immigration", "border security",
            "skills-based", "controlled immigration", "enforce immigration law"
        ],
        references=[
            AcademicReference(
                author="Political Science View",
                title="Democrats vs Republicans: Party Policies",
                year=2024,
                source_type="article",
                url="https://www.politicalscienceview.com/democrats-vs-republicans-us-party-policies/"
            )
        ],
        category="immigration",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article support strict immigration enforcement and reducing legal immigration?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "reduce immigration", "build the wall", "deport illegals",
            "immigration hurts", "immigration enforcement", "secure borders"
        ],
        references=[
            AcademicReference(
                author="Political Science View",
                title="Democrats vs Republicans: Party Policies",
                year=2024,
                source_type="article"
            )
        ],
        category="immigration",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article use dehumanizing language about immigrants (invasion, infestation, etc.)?",
        yes_maps_to="Strong Traditional Conservative",
        yes_score=10.0,
        keywords=[
            "immigrant invasion", "illegal alien", "infestation",
            "replacement", "immigrant crime wave", "foreign horde"
        ],
        references=[
            AcademicReference(
                author="ADL",
                title="Analysis of extremist anti-immigrant rhetoric",
                year=2024,
                source_type="institution"
            )
        ],
        category="immigration",
        weight=1.0,
        notes="Dehumanizing language indicates extreme position"
    ),

    # =========================================================================
    # CLIMATE CHANGE / ENVIRONMENT
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support immediate, drastic action on climate change (e.g., ban fossil fuels)?",
        yes_maps_to="Strong Progressive",
        yes_score=-10.0,
        keywords=[
            "climate emergency", "ban fossil fuels", "net zero immediately",
            "climate crisis", "extinction rebellion", "end oil now"
        ],
        references=[
            AcademicReference(
                author="IPCC",
                title="Climate Change 2023: Synthesis Report",
                year=2023,
                source_type="institution"
            )
        ],
        category="climate",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support significant government action on climate change?",
        yes_maps_to="Progressive",
        yes_score=-7.5,
        keywords=[
            "climate action", "renewable energy", "carbon tax",
            "paris agreement", "green energy", "climate policy"
        ],
        references=[
            AcademicReference(
                author="Pew Research Center",
                title="Climate change views by party",
                year=2018,
                source_type="article"
            )
        ],
        category="climate",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article acknowledge climate change but prioritize economic concerns?",
        yes_maps_to="Mild Conservative",
        yes_score=2.5,
        keywords=[
            "balanced approach climate", "economic impact climate policy",
            "gradual transition", "energy independence", "all of the above energy"
        ],
        references=[
            AcademicReference(
                author="Political Science View",
                title="Democrats vs Republicans: Party Policies",
                year=2024,
                source_type="article"
            )
        ],
        category="climate",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article express skepticism about climate science or oppose climate regulations?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "climate skeptic", "climate hoax", "no climate regulations",
            "climate alarmism", "drill baby drill", "war on coal"
        ],
        references=[
            AcademicReference(
                author="Pew Research Center",
                title="Political polarization on climate",
                year=2018,
                source_type="article"
            )
        ],
        category="climate",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article deny human-caused climate change entirely?",
        yes_maps_to="Strong Traditional Conservative",
        yes_score=10.0,
        keywords=[
            "climate denial", "no global warming", "climate is natural",
            "climate fraud", "scientists lying", "no human impact climate"
        ],
        references=[
            AcademicReference(
                author="Cook, J. et al.",
                title="Quantifying the consensus on anthropogenic global warming",
                year=2013,
                source_type="article"
            )
        ],
        category="climate",
        weight=1.0,
        notes="Denial of scientific consensus indicates extreme position"
    ),

    # =========================================================================
    # RACIAL JUSTICE / SOCIAL JUSTICE
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support reparations for slavery and systemic racism?",
        yes_maps_to="Strong Progressive",
        yes_score=-10.0,
        keywords=[
            "reparations", "systemic racism", "racial justice",
            "structural racism", "white supremacy", "antiracism"
        ],
        references=[
            AcademicReference(
                author="Coates, T.",
                title="The Case for Reparations",
                year=2014,
                source_type="article"
            )
        ],
        category="racial_justice",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support police reform or defunding police?",
        yes_maps_to="Progressive",
        yes_score=-7.5,
        keywords=[
            "defund police", "police reform", "black lives matter",
            "police brutality", "abolish police", "reimagine public safety"
        ],
        references=[
            AcademicReference(
                author="Kendi, I.X.",
                title="How to Be an Antiracist",
                year=2019,
                source_type="book"
            )
        ],
        category="racial_justice",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support 'law and order' policies and increased police funding?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "law and order", "back the blue", "support police",
            "tough on crime", "more police", "fund the police"
        ],
        references=[
            AcademicReference(
                author="Heritage Foundation",
                title="Crime and Justice publications",
                year=2024,
                source_type="institution"
            )
        ],
        category="racial_justice",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article deny the existence of systemic racism or oppose DEI initiatives?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "no systemic racism", "reverse racism", "anti-woke",
            "critical race theory bad", "dei is racist", "colorblind"
        ],
        references=[
            AcademicReference(
                author="Sowell, T.",
                title="Discrimination and Disparities",
                year=2018,
                source_type="book"
            )
        ],
        category="racial_justice",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article use racist dog whistles or promote white identity politics?",
        yes_maps_to="Strong Traditional Conservative",
        yes_score=10.0,
        keywords=[
            "white genocide", "great replacement", "white identity",
            "western civilization threatened", "demographic replacement"
        ],
        references=[
            AcademicReference(
                author="SPLC",
                title="Hate group tracking",
                year=2024,
                source_type="institution"
            )
        ],
        category="racial_justice",
        weight=1.0,
        notes="Explicit racism indicates extreme position"
    ),

    # =========================================================================
    # GUN RIGHTS / GUN CONTROL
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support banning all or most firearms?",
        yes_maps_to="Strong Progressive",
        yes_score=-10.0,
        keywords=[
            "ban guns", "repeal second amendment", "no civilian guns",
            "disarm america", "gun confiscation"
        ],
        references=[
            AcademicReference(
                author="Pew Research Center",
                title="Gun policy views by party",
                year=2018,
                source_type="article"
            )
        ],
        category="guns",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support assault weapons bans, universal background checks, or red flag laws?",
        yes_maps_to="Progressive",
        yes_score=-7.5,
        keywords=[
            "assault weapons ban", "universal background checks", "red flag laws",
            "gun control", "common sense gun laws", "gun safety"
        ],
        references=[
            AcademicReference(
                author="Giffords Law Center",
                title="Gun law research",
                year=2024,
                source_type="institution"
            )
        ],
        category="guns",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support gun rights with some regulations (current laws sufficient)?",
        yes_maps_to="Mild Conservative",
        yes_score=2.5,
        keywords=[
            "responsible gun ownership", "enforce existing laws",
            "second amendment rights", "gun safety education"
        ],
        references=[
            AcademicReference(
                author="Pew Research Center",
                title="Gun policy views",
                year=2018,
                source_type="article"
            )
        ],
        category="guns",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article oppose most gun regulations as unconstitutional?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "shall not be infringed", "gun rights", "second amendment absolute",
            "oppose gun control", "armed citizenry", "nra"
        ],
        references=[
            AcademicReference(
                author="NRA-ILA",
                title="Second Amendment advocacy",
                year=2024,
                source_type="institution"
            )
        ],
        category="guns",
        weight=1.0
    ),

    IdeologyQuestion(
        question="Does this article support eliminating all gun regulations including background checks?",
        yes_maps_to="Strong Traditional Conservative",
        yes_score=10.0,
        keywords=[
            "no gun laws", "constitutional carry everywhere",
            "abolish atf", "all gun laws unconstitutional"
        ],
        references=[
            AcademicReference(
                author="Gun Owners of America",
                title="No compromise gun rights",
                year=2024,
                source_type="institution"
            )
        ],
        category="guns",
        weight=1.0
    ),

    # =========================================================================
    # RELIGION IN PUBLIC LIFE
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support strict separation of church and state?",
        yes_maps_to="Progressive",
        yes_score=-7.5,
        keywords=[
            "separation church state", "secular government", "no religion in government",
            "secular society", "religious freedom means freedom from religion"
        ],
        references=[
            AcademicReference(
                author="Americans United for Separation of Church and State",
                title="Church-state separation advocacy",
                year=2024,
                source_type="institution"
            )
        ],
        category="religion",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article support prayer in public schools or religious displays on government property?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "prayer in schools", "christian nation", "ten commandments",
            "religious heritage", "god in public", "faith in government"
        ],
        references=[
            AcademicReference(
                author="Wikipedia",
                title="Social conservatism",
                year=2024,
                source_type="encyclopedia"
            )
        ],
        category="religion",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article advocate for laws based explicitly on religious doctrine?",
        yes_maps_to="Strong Traditional Conservative",
        yes_score=10.0,
        keywords=[
            "biblical law", "christian nationalism", "religious law",
            "god's law above man's", "theocracy", "dominionism"
        ],
        references=[
            AcademicReference(
                author="Whitehead, A. & Perry, S.",
                title="Taking America Back for God: Christian Nationalism in the United States",
                year=2020,
                source_type="book"
            )
        ],
        category="religion",
        weight=1.0
    ),

    # =========================================================================
    # GENDER ROLES / FEMINISM
    # =========================================================================
    IdeologyQuestion(
        question="Does this article support dismantling traditional gender roles entirely?",
        yes_maps_to="Strong Progressive",
        yes_score=-10.0,
        keywords=[
            "abolish gender", "gender is social construct", "smash patriarchy",
            "toxic masculinity", "gender abolition"
        ],
        references=[
            AcademicReference(
                author="Butler, J.",
                title="Gender Trouble",
                year=1990,
                source_type="book"
            )
        ],
        category="gender",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article support equal pay legislation and addressing workplace gender discrimination?",
        yes_maps_to="Progressive",
        yes_score=-7.5,
        keywords=[
            "equal pay", "gender pay gap", "workplace discrimination",
            "glass ceiling", "women's rights", "feminism"
        ],
        references=[
            AcademicReference(
                author="Pew Research Center",
                title="Gender and work",
                year=2024,
                source_type="article"
            )
        ],
        category="gender",
        weight=0.8
    ),

    IdeologyQuestion(
        question="Does this article support traditional gender roles as natural or beneficial?",
        yes_maps_to="Traditional Conservative",
        yes_score=7.5,
        keywords=[
            "traditional gender roles", "natural differences", "men and women different",
            "traditional family", "mother's role", "father's role"
        ],
        references=[
            AcademicReference(
                author="Wikipedia",
                title="Social conservatism",
                year=2024,
                source_type="encyclopedia"
            )
        ],
        category="gender",
        weight=0.9
    ),

    IdeologyQuestion(
        question="Does this article argue that feminism is harmful or that women should primarily be homemakers?",
        yes_maps_to="Strong Traditional Conservative",
        yes_score=10.0,
        keywords=[
            "feminism is cancer", "women belong home", "reject feminism",
            "traditional womanhood", "anti-feminist", "mens rights"
        ],
        references=[
            AcademicReference(
                author="Various",
                title="Anti-feminist literature",
                year=2024,
                source_type="article"
            )
        ],
        category="gender",
        weight=1.0
    ),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_questions_by_category(
    questions: List[IdeologyQuestion],
    category: str
) -> List[IdeologyQuestion]:
    """Filter questions by category."""
    return [q for q in questions if q.category == category]


def get_questions_by_score_range(
    questions: List[IdeologyQuestion],
    min_score: float,
    max_score: float
) -> List[IdeologyQuestion]:
    """Filter questions by score range."""
    return [q for q in questions if min_score <= q.yes_score <= max_score]


def get_all_keywords(questions: List[IdeologyQuestion]) -> List[str]:
    """Extract all unique keywords from questions."""
    keywords = set()
    for q in questions:
        keywords.update(q.keywords)
    return sorted(list(keywords))


def get_economic_keywords() -> List[str]:
    """Get all economic keywords for article search."""
    return get_all_keywords(ECONOMIC_QUESTIONS)


def get_social_keywords() -> List[str]:
    """Get all social keywords for article search."""
    return get_all_keywords(SOCIAL_QUESTIONS)


# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("IDEOLOGY QUESTION BANK SUMMARY")
    print("=" * 70)

    print(f"\nECONOMIC QUESTIONS: {len(ECONOMIC_QUESTIONS)}")
    print("-" * 40)

    # Group by ideology
    economic_by_ideology = {}
    for q in ECONOMIC_QUESTIONS:
        ideology = q.yes_maps_to
        if ideology not in economic_by_ideology:
            economic_by_ideology[ideology] = []
        economic_by_ideology[ideology].append(q)

    for ideology, qs in sorted(economic_by_ideology.items(), key=lambda x: x[1][0].yes_score if x[1] else 0):
        score = qs[0].yes_score if qs else 0
        print(f"  {ideology} ({score:+.1f}): {len(qs)} questions")

    print(f"\nSOCIAL QUESTIONS: {len(SOCIAL_QUESTIONS)}")
    print("-" * 40)

    social_by_ideology = {}
    for q in SOCIAL_QUESTIONS:
        ideology = q.yes_maps_to
        if ideology not in social_by_ideology:
            social_by_ideology[ideology] = []
        social_by_ideology[ideology].append(q)

    for ideology, qs in sorted(social_by_ideology.items(), key=lambda x: x[1][0].yes_score if x[1] else 0):
        score = qs[0].yes_score if qs else 0
        print(f"  {ideology} ({score:+.1f}): {len(qs)} questions")

    print(f"\nTOTAL QUESTIONS: {len(ECONOMIC_QUESTIONS) + len(SOCIAL_QUESTIONS)}")
    print(f"TOTAL ECONOMIC KEYWORDS: {len(get_economic_keywords())}")
    print(f"TOTAL SOCIAL KEYWORDS: {len(get_social_keywords())}")

    print("\n" + "=" * 70)
    print("ACADEMIC REFERENCES USED")
    print("=" * 70)

    all_refs = set()
    for q in ECONOMIC_QUESTIONS + SOCIAL_QUESTIONS:
        for ref in q.references:
            all_refs.add(str(ref))

    for ref in sorted(all_refs):
        print(f"  - {ref}")
