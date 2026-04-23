import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown, Minus, PieChart as PieChartIcon, BarChart3, AlertTriangle } from 'lucide-react';
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface RealtimePnl {
    floating_pnl: number;
    floating_pnl_pct: number;
    today_pnl: number;
    today_pnl_pct: number;
    total_pnl: number;
    total_pnl_pct: number;
    win_rate: number;
    profitable_count: number;
    losing_count: number;
    total_position_count: number;
}

interface IndustryDistribution {
    industry: string;
    weight: number;
    value: number;
    position_count: number;
}

interface TopHolding {
    symbol: string;
    name: string;
    weight: number;
    market_value: number;
}

interface RiskExposure {
    long_exposure: number;
    short_exposure: number;
    net_exposure: number;
    long_value: number;
    short_value: number;
}

interface PositionStructure {
    industry_distribution: IndustryDistribution[];
    sector_concentration: Record<string, number>;
    risk_exposure: RiskExposure;
    position_count: number;
    top_holdings: TopHolding[];
}

interface AccountingData {
    realtime_pnl?: RealtimePnl;
    structure?: PositionStructure;
}

interface PositionAccountingCardProps {
    accounting?: AccountingData;
    totalAsset?: number;
    className?: string;
}

const formatAmount = (val: number) => {
    if (Math.abs(val) >= 10000) {
        return `¥${(val / 10000).toFixed(2)}万`;
    }
    return `¥${val.toFixed(2)}`;
};

const formatPercent = (val: number) => {
    const pct = val * 100;
    return `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`;
};

const INDUSTRY_COLORS: Record<string, string> = {
    '银行': '#1E3A8A',
    '证券': '#3B82F6',
    '保险': '#60A5FA',
    '金融': '#1E3A8A',
    '计算机': '#059669',
    '电子': '#10B981',
    '通信': '#34D399',
    '传媒': '#6EE7B7',
    '科技': '#059669',
    '食品饮料': '#DC2626',
    '家用电器': '#F87171',
    '纺织服装': '#EF4444',
    '商贸零售': '#FB923C',
    '医药生物': '#F97316',
    '消费': '#DC2626',
    '机械设备': '#7C3AED',
    '电气设备': '#8B5CF6',
    '汽车': '#A78BFA',
    '化工': '#C4B5FD',
    '制造': '#7C3AED',
    '建筑装饰': '#D97706',
    '建筑材料': '#F59E0B',
    '房地产': '#FBBF24',
    '公用事业': '#FCD34D',
    '交通运输': '#CA8A04',
    '基建': '#D97706',
    '采掘': '#475569',
    '石油石化': '#64748B',
    '煤炭': '#94A3B8',
    '电力': '#CBD5E1',
    '能源': '#475569',
    '其他': '#9CA3AF',
};

const PositionAccountingCard: React.FC<PositionAccountingCardProps> = ({
    accounting,
    totalAsset,
    className,
}) => {
    const realtimePnl = accounting?.realtime_pnl;
    const structure = accounting?.structure;

    const pnlMetrics = useMemo(() => {
        if (!realtimePnl) return null;
        return {
            floating: {
                value: realtimePnl.floating_pnl || 0,
                pct: realtimePnl.floating_pnl_pct || 0,
            },
            today: {
                value: realtimePnl.today_pnl || 0,
                pct: realtimePnl.today_pnl_pct || 0,
            },
            total: {
                value: realtimePnl.total_pnl || 0,
                pct: realtimePnl.total_pnl_pct || 0,
            },
            winRate: realtimePnl.win_rate || 0,
            profitable: realtimePnl.profitable_count || 0,
            losing: realtimePnl.losing_count || 0,
        };
    }, [realtimePnl]);

    const industryChartData = useMemo(() => {
        if (!structure?.industry_distribution) return [];
        return structure.industry_distribution
            .filter(item => item.weight > 0)
            .map(item => ({
                name: item.industry || '其他',
                value: item.value,
                weight: item.weight,
                color: INDUSTRY_COLORS[item.industry] || '#9CA3AF',
            }));
    }, [structure]);

    const hasIndustryData = industryChartData.length > 0 && industryChartData.some(d => d.value > 0);

    if (!accounting) {
        return (
            <div className={`bg-white rounded-xl p-4 border border-gray-200 ${className || ''}`}>
                <div className="text-sm text-gray-400 text-center py-4">
                    暂无核算数据
                </div>
            </div>
        );
    }

    return (
        <div className={`bg-white rounded-xl border border-gray-200 overflow-hidden ${className || ''}`}>
            {/* 盈亏核算区域 */}
            <div className="p-4 border-b border-gray-100">
                <h3 className="text-sm font-bold text-gray-800 mb-3 flex items-center">
                    <BarChart3 className="mr-2 text-blue-600" size={16} />
                    实时盈亏核算
                </h3>

                {pnlMetrics && (
                    <div className="grid grid-cols-4 gap-3">
                        {/* 浮动盈亏 */}
                        <div className="bg-gray-50 rounded-lg p-2.5">
                            <div className="text-xs text-gray-500 mb-1">浮动盈亏</div>
                            <div className={`text-sm font-bold flex items-center gap-1 ${
                                pnlMetrics.floating.value > 0 ? 'text-red-500' :
                                pnlMetrics.floating.value < 0 ? 'text-emerald-500' : 'text-gray-900'
                            }`}>
                                {pnlMetrics.floating.value > 0 ? <TrendingUp size={12} /> :
                                 pnlMetrics.floating.value < 0 ? <TrendingDown size={12} /> : <Minus size={12} />}
                                {pnlMetrics.floating.value > 0 ? '+' : ''}{formatAmount(pnlMetrics.floating.value)}
                            </div>
                            <div className={`text-xs ${
                                pnlMetrics.floating.pct > 0 ? 'text-red-400' :
                                pnlMetrics.floating.pct < 0 ? 'text-emerald-400' : 'text-gray-500'
                            }`}>
                                {formatPercent(pnlMetrics.floating.pct)}
                            </div>
                        </div>

                        {/* 今日盈亏 */}
                        <div className="bg-gray-50 rounded-lg p-2.5">
                            <div className="text-xs text-gray-500 mb-1">今日盈亏</div>
                            <div className={`text-sm font-bold flex items-center gap-1 ${
                                pnlMetrics.today.value > 0 ? 'text-red-500' :
                                pnlMetrics.today.value < 0 ? 'text-emerald-500' : 'text-gray-900'
                            }`}>
                                {pnlMetrics.today.value > 0 ? <TrendingUp size={12} /> :
                                 pnlMetrics.today.value < 0 ? <TrendingDown size={12} /> : <Minus size={12} />}
                                {pnlMetrics.today.value > 0 ? '+' : ''}{formatAmount(pnlMetrics.today.value)}
                            </div>
                            <div className={`text-xs ${
                                pnlMetrics.today.pct > 0 ? 'text-red-400' :
                                pnlMetrics.today.pct < 0 ? 'text-emerald-400' : 'text-gray-500'
                            }`}>
                                {formatPercent(pnlMetrics.today.pct)}
                            </div>
                        </div>

                        {/* 累计盈亏 */}
                        <div className="bg-gray-50 rounded-lg p-2.5">
                            <div className="text-xs text-gray-500 mb-1">累计盈亏</div>
                            <div className={`text-sm font-bold flex items-center gap-1 ${
                                pnlMetrics.total.value > 0 ? 'text-red-500' :
                                pnlMetrics.total.value < 0 ? 'text-emerald-500' : 'text-gray-900'
                            }`}>
                                {pnlMetrics.total.value > 0 ? <TrendingUp size={12} /> :
                                 pnlMetrics.total.value < 0 ? <TrendingDown size={12} /> : <Minus size={12} />}
                                {pnlMetrics.total.value > 0 ? '+' : ''}{formatAmount(pnlMetrics.total.value)}
                            </div>
                            <div className={`text-xs ${
                                pnlMetrics.total.pct > 0 ? 'text-red-400' :
                                pnlMetrics.total.pct < 0 ? 'text-emerald-400' : 'text-gray-500'
                            }`}>
                                {formatPercent(pnlMetrics.total.pct)}
                            </div>
                        </div>

                        {/* 胜率 */}
                        <div className="bg-gray-50 rounded-lg p-2.5">
                            <div className="text-xs text-gray-500 mb-1">持仓胜率</div>
                            <div className="text-sm font-bold text-gray-900">
                                {(pnlMetrics.winRate * 100).toFixed(1)}%
                            </div>
                            <div className="text-xs text-gray-500">
                                {pnlMetrics.profitable}盈 / {pnlMetrics.losing}亏
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* 行业分布区域 */}
            <div className="p-4 border-b border-gray-100">
                <h3 className="text-sm font-bold text-gray-800 mb-3 flex items-center">
                    <PieChartIcon className="mr-2 text-blue-600" size={16} />
                    行业分布
                </h3>

                <div className="flex gap-4">
                    {/* 饼图 */}
                    <div className="w-[40%] h-[120px] relative">
                        {hasIndustryData ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <RechartsPieChart>
                                    <Pie
                                        data={industryChartData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={35}
                                        outerRadius={50}
                                        paddingAngle={2}
                                        dataKey="value"
                                    >
                                        {industryChartData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        formatter={(value: number) => formatAmount(value)}
                                        contentStyle={{
                                            backgroundColor: '#fff',
                                            borderColor: '#e5e7eb',
                                            borderRadius: '8px',
                                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                        }}
                                    />
                                </RechartsPieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex items-center justify-center text-gray-400 text-xs">
                                暂无行业数据
                            </div>
                        )}
                    </div>

                    {/* 行业列表 */}
                    <div className="w-[60%] overflow-y-auto max-h-[120px] custom-scrollbar">
                        {structure?.industry_distribution && structure.industry_distribution.length > 0 ? (
                            <div className="space-y-1">
                                {structure.industry_distribution.slice(0, 6).map((item, idx) => (
                                    <div key={idx} className="flex items-center justify-between text-xs">
                                        <div className="flex items-center gap-1.5">
                                            <span
                                                className="w-2 h-2 rounded-full"
                                                style={{ backgroundColor: INDUSTRY_COLORS[item.industry] || '#9CA3AF' }}
                                            />
                                            <span className="text-gray-700">{item.industry}</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-gray-500">
                                                {(item.weight * 100).toFixed(1)}%
                                            </span>
                                            <span className="text-gray-900 font-medium">
                                                {formatAmount(item.value)}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-xs text-gray-400 text-center py-4">
                                暂无行业分布数据
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* 风险敞口区域 */}
            {structure?.risk_exposure && (
                <div className="p-4">
                    <h3 className="text-sm font-bold text-gray-800 mb-3 flex items-center">
                        <AlertTriangle className="mr-2 text-amber-500" size={16} />
                        风险敞口
                    </h3>

                    <div className="grid grid-cols-3 gap-3">
                        <div className="bg-green-50 rounded-lg p-2">
                            <div className="text-xs text-green-600 mb-1">多头敞口</div>
                            <div className="text-sm font-bold text-green-700">
                                {(structure.risk_exposure.long_exposure * 100).toFixed(1)}%
                            </div>
                            <div className="text-xs text-green-600">
                                {formatAmount(structure.risk_exposure.long_value)}
                            </div>
                        </div>

                        <div className="bg-red-50 rounded-lg p-2">
                            <div className="text-xs text-red-600 mb-1">空头敞口</div>
                            <div className="text-sm font-bold text-red-700">
                                {(structure.risk_exposure.short_exposure * 100).toFixed(1)}%
                            </div>
                            <div className="text-xs text-red-600">
                                {formatAmount(structure.risk_exposure.short_value)}
                            </div>
                        </div>

                        <div className="bg-blue-50 rounded-lg p-2">
                            <div className="text-xs text-blue-600 mb-1">净敞口</div>
                            <div className="text-sm font-bold text-blue-700">
                                {(structure.risk_exposure.net_exposure * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>

                    {/* Top持仓 */}
                    {structure.top_holdings && structure.top_holdings.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-100">
                            <div className="text-xs text-gray-500 mb-2">Top持仓</div>
                            <div className="flex flex-wrap gap-2">
                                {structure.top_holdings.slice(0, 5).map((holding, idx) => (
                                    <div
                                        key={idx}
                                        className="bg-gray-50 rounded px-2 py-1 text-xs flex items-center gap-1"
                                    >
                                        <span className="font-medium text-gray-700">
                                            {holding.name || holding.symbol}
                                        </span>
                                        <span className="text-gray-500">
                                            {(holding.weight * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default PositionAccountingCard;