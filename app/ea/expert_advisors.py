"""
Sistema de Expert Advisors (EA) tipo MetaTrader 4/5 para trading automático.
Permite crear estrategias configurables con reglas de entrada, salida y gestión de riesgo.
"""
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime


class SignalType(Enum):
    """Tipos de señal de trading"""
    BUY = "BUY"
    SELL = "SELL"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"
    HOLD = "HOLD"


class OrderType(Enum):
    """Tipos de orden"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


@dataclass
class Trade:
    """Representa una operación de trading"""
    entry_date: str
    entry_price: float
    signal_type: SignalType
    size: float = 1.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    reason: str = ""


@dataclass
class EAConfig:
    """Configuración de un Expert Advisor"""
    name: str
    description: str
    
    # Parámetros de indicadores
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70
    
    sma_fast: int = 20
    sma_slow: int = 50
    
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    bb_period: int = 20
    bb_std: float = 2.0
    
    # Gestión de riesgo
    risk_per_trade: float = 2.0  # % del capital por operación
    max_open_trades: int = 3
    stop_loss_pct: float = 3.0  # % de stop loss
    take_profit_pct: float = 6.0  # % de take profit
    trailing_stop_pct: Optional[float] = None  # % de trailing stop
    
    # Filtros
    min_score: float = 6.0  # Score Danelfin mínimo para operar
    volume_filter: bool = True  # Filtrar por volumen
    trend_filter: bool = True  # Solo operar a favor de la tendencia
    
    # Timeframe
    timeframe: str = "1D"  # 1D, 4H, 1H, etc.


class ExpertAdvisor:
    """
    Expert Advisor base tipo MetaTrader.
    Implementa lógica de trading automático con reglas configurables.
    """
    
    def __init__(self, config: EAConfig):
        self.config = config
        self.trades: List[Trade] = []
        self.open_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        
    def analyze(self, data: pd.DataFrame, current_score: Optional[float] = None) -> Dict:
        """
        Analiza el mercado y genera señales de trading.
        
        Args:
            data: DataFrame con datos OHLCV e indicadores
            current_score: Score Danelfin actual (opcional)
            
        Returns:
            Dict con señal y detalles
        """
        if len(data) < max(self.config.sma_slow, 50):
            return {
                'signal': SignalType.HOLD,
                'confidence': 0.0,
                'reason': 'Datos insuficientes',
                'price': None,
                'stop_loss': None,
                'take_profit': None
            }
        
        latest = data.iloc[-1]
        
        # Filtro por score Danelfin
        if current_score is not None and current_score < self.config.min_score:
            return {
                'signal': SignalType.HOLD,
                'confidence': 0.0,
                'reason': f'Score insuficiente ({current_score:.1f} < {self.config.min_score})',
                'price': latest['close'],
                'stop_loss': None,
                'take_profit': None
            }
        
        # Aplicar estrategia
        signal_data = self._generate_signal(data, latest)
        
        # Gestión de operaciones abiertas
        if self.open_trades:
            self._manage_open_trades(latest)
        
        return signal_data
    
    def _generate_signal(self, data: pd.DataFrame, latest: pd.Series) -> Dict:
        """Genera señal de trading basada en la estrategia"""
        raise NotImplementedError("Debe implementarse en subclases")
    
    def _manage_open_trades(self, latest: pd.Series):
        """Gestiona operaciones abiertas: stop loss, take profit, trailing stop"""
        current_price = latest['close']
        
        for trade in self.open_trades[:]:
            should_close = False
            close_reason = ""
            
            # Stop Loss
            if trade.stop_loss and current_price <= trade.stop_loss:
                should_close = True
                close_reason = f"Stop Loss alcanzado ({trade.stop_loss:.2f})"
            
            # Take Profit
            elif trade.take_profit and current_price >= trade.take_profit:
                should_close = True
                close_reason = f"Take Profit alcanzado ({trade.take_profit:.2f})"
            
            # Trailing Stop
            elif self.config.trailing_stop_pct:
                if trade.signal_type == SignalType.BUY:
                    # Actualizar stop loss si el precio sube
                    new_stop = current_price * (1 - self.config.trailing_stop_pct / 100)
                    if not trade.stop_loss or new_stop > trade.stop_loss:
                        trade.stop_loss = new_stop
            
            if should_close:
                self._close_trade(trade, current_price, latest['date'] if 'date' in latest else str(datetime.now().date()), close_reason)
    
    def _close_trade(self, trade: Trade, exit_price: float, exit_date: str, reason: str):
        """Cierra una operación"""
        trade.exit_price = exit_price
        trade.exit_date = exit_date
        trade.reason = reason
        
        if trade.signal_type == SignalType.BUY:
            trade.profit_loss = (exit_price - trade.entry_price) * trade.size
            trade.profit_loss_pct = ((exit_price / trade.entry_price) - 1) * 100
        else:  # SELL
            trade.profit_loss = (trade.entry_price - exit_price) * trade.size
            trade.profit_loss_pct = ((trade.entry_price / exit_price) - 1) * 100
        
        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 10000) -> Dict:
        """
        Realiza backtest de la estrategia.
        
        Args:
            data: DataFrame histórico con OHLCV e indicadores
            initial_capital: Capital inicial en EUR
            
        Returns:
            Dict con resultados del backtest
        """
        capital = initial_capital
        equity_curve = []
        self.open_trades = []
        self.closed_trades = []
        
        for i in range(max(self.config.sma_slow, 50), len(data)):
            current_data = data.iloc[:i+1]
            latest = current_data.iloc[-1]
            current_price = latest['close']
            
            # Gestionar operaciones abiertas
            self._manage_open_trades(latest)
            
            # Generar señal
            signal_data = self._generate_signal(current_data, latest)
            
            # Ejecutar señal si hay capital y no excede límite de operaciones
            if len(self.open_trades) < self.config.max_open_trades:
                if signal_data['signal'] == SignalType.BUY and capital > 0:
                    position_size = (capital * self.config.risk_per_trade / 100) / current_price
                    
                    trade = Trade(
                        entry_date=latest['date'] if 'date' in latest else str(i),
                        entry_price=current_price,
                        signal_type=SignalType.BUY,
                        size=position_size,
                        stop_loss=signal_data.get('stop_loss'),
                        take_profit=signal_data.get('take_profit'),
                        reason=signal_data.get('reason', '')
                    )
                    
                    self.open_trades.append(trade)
                    capital -= current_price * position_size
            
            # Calcular equity
            open_pl = sum((current_price - t.entry_price) * t.size for t in self.open_trades)
            closed_pl = sum(t.profit_loss for t in self.closed_trades if t.profit_loss)
            total_equity = capital + open_pl + (closed_pl if closed_pl else 0)
            
            equity_curve.append({
                'date': latest['date'] if 'date' in latest else str(i),
                'equity': total_equity,
                'capital': capital,
                'open_trades': len(self.open_trades),
                'closed_trades': len(self.closed_trades)
            })
        
        # Cerrar operaciones abiertas al final
        final_price = data.iloc[-1]['close']
        final_date = data.iloc[-1]['date'] if 'date' in data.iloc[-1] else str(len(data)-1)
        for trade in self.open_trades[:]:
            self._close_trade(trade, final_price, final_date, "Fin del backtest")
        
        return self._calculate_backtest_metrics(initial_capital, equity_curve)
    
    def _calculate_backtest_metrics(self, initial_capital: float, equity_curve: List[Dict]) -> Dict:
        """Calcula métricas del backtest"""
        if not self.closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_return': 0.0,
                'total_return_pct': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'equity_curve': equity_curve
            }
        
        winning_trades = [t for t in self.closed_trades if t.profit_loss and t.profit_loss > 0]
        losing_trades = [t for t in self.closed_trades if t.profit_loss and t.profit_loss <= 0]
        
        total_profit = sum(t.profit_loss for t in winning_trades)
        total_loss = abs(sum(t.profit_loss for t in losing_trades))
        
        final_equity = equity_curve[-1]['equity'] if equity_curve else initial_capital
        total_return = final_equity - initial_capital
        
        # Calcular drawdown
        equity_values = [e['equity'] for e in equity_curve]
        peak = equity_values[0]
        max_dd = 0
        for equity in equity_values:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        # Sharpe Ratio simplificado
        returns = [equity_values[i] / equity_values[i-1] - 1 
                  for i in range(1, len(equity_values))]
        sharpe = 0.0
        if returns and np.std(returns) > 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)  # Anualizado
        
        return {
            'total_trades': len(self.closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.closed_trades) * 100 if self.closed_trades else 0,
            'total_return': total_return,
            'total_return_pct': (total_return / initial_capital) * 100,
            'max_drawdown': max_dd,
            'sharpe_ratio': sharpe,
            'avg_win': total_profit / len(winning_trades) if winning_trades else 0,
            'avg_loss': total_loss / len(losing_trades) if losing_trades else 0,
            'profit_factor': total_profit / total_loss if total_loss > 0 else 0,
            'equity_curve': equity_curve,
            'trades': [
                {
                    'entry_date': t.entry_date,
                    'entry_price': t.entry_price,
                    'exit_date': t.exit_date,
                    'exit_price': t.exit_price,
                    'profit_loss': t.profit_loss,
                    'profit_loss_pct': t.profit_loss_pct,
                    'reason': t.reason
                }
                for t in self.closed_trades[-10:]  # Últimas 10 operaciones
            ]
        }


class RSI_EA(ExpertAdvisor):
    """Expert Advisor basado en RSI"""
    
    def _generate_signal(self, data: pd.DataFrame, latest: pd.Series) -> Dict:
        current_price = latest['close']
        rsi = latest.get('rsi')
        
        if pd.isna(rsi):
            return {
                'signal': SignalType.HOLD,
                'confidence': 0.0,
                'reason': 'RSI no disponible',
                'price': current_price,
                'stop_loss': None,
                'take_profit': None
            }
        
        # Señales
        if rsi < self.config.rsi_oversold:
            return {
                'signal': SignalType.BUY,
                'confidence': (self.config.rsi_oversold - rsi) / self.config.rsi_oversold,
                'reason': f'RSI en sobreventa ({rsi:.1f})',
                'price': current_price,
                'stop_loss': current_price * (1 - self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 + self.config.take_profit_pct / 100)
            }
        elif rsi > self.config.rsi_overbought:
            return {
                'signal': SignalType.SELL,
                'confidence': (rsi - self.config.rsi_overbought) / (100 - self.config.rsi_overbought),
                'reason': f'RSI en sobrecompra ({rsi:.1f})',
                'price': current_price,
                'stop_loss': current_price * (1 + self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 - self.config.take_profit_pct / 100)
            }
        
        return {
            'signal': SignalType.HOLD,
            'confidence': 0.0,
            'reason': f'RSI neutral ({rsi:.1f})',
            'price': current_price,
            'stop_loss': None,
            'take_profit': None
        }


class MACD_EA(ExpertAdvisor):
    """Expert Advisor basado en MACD"""
    
    def _generate_signal(self, data: pd.DataFrame, latest: pd.Series) -> Dict:
        current_price = latest['close']
        macd = latest.get('macd')
        macd_signal = latest.get('macd_signal')
        
        if pd.isna(macd) or pd.isna(macd_signal) or len(data) < 2:
            return {
                'signal': SignalType.HOLD,
                'confidence': 0.0,
                'reason': 'MACD no disponible',
                'price': current_price,
                'stop_loss': None,
                'take_profit': None
            }
        
        prev_macd = data['macd'].iloc[-2]
        prev_signal = data['macd_signal'].iloc[-2]
        
        # Cruce alcista
        if prev_macd <= prev_signal and macd > macd_signal:
            return {
                'signal': SignalType.BUY,
                'confidence': min(abs(macd - macd_signal) / abs(macd), 1.0),
                'reason': 'MACD cruzó al alza',
                'price': current_price,
                'stop_loss': current_price * (1 - self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 + self.config.take_profit_pct / 100)
            }
        
        # Cruce bajista
        elif prev_macd >= prev_signal and macd < macd_signal:
            return {
                'signal': SignalType.SELL,
                'confidence': min(abs(macd - macd_signal) / abs(macd), 1.0),
                'reason': 'MACD cruzó a la baja',
                'price': current_price,
                'stop_loss': current_price * (1 + self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 - self.config.take_profit_pct / 100)
            }
        
        return {
            'signal': SignalType.HOLD,
            'confidence': 0.0,
            'reason': 'Sin cruce MACD',
            'price': current_price,
            'stop_loss': None,
            'take_profit': None
        }


class MA_Crossover_EA(ExpertAdvisor):
    """Expert Advisor basado en cruce de medias móviles (Golden Cross / Death Cross)"""
    
    def _generate_signal(self, data: pd.DataFrame, latest: pd.Series) -> Dict:
        current_price = latest['close']
        sma_fast = latest.get('sma_20')
        sma_slow = latest.get('sma_50')
        
        if pd.isna(sma_fast) or pd.isna(sma_slow) or len(data) < 2:
            return {
                'signal': SignalType.HOLD,
                'confidence': 0.0,
                'reason': 'Medias móviles no disponibles',
                'price': current_price,
                'stop_loss': None,
                'take_profit': None
            }
        
        prev_fast = data['sma_20'].iloc[-2]
        prev_slow = data['sma_50'].iloc[-2]
        
        # Golden Cross
        if prev_fast <= prev_slow and sma_fast > sma_slow:
            return {
                'signal': SignalType.BUY,
                'confidence': min((sma_fast - sma_slow) / sma_slow * 10, 1.0),
                'reason': 'Golden Cross detectado',
                'price': current_price,
                'stop_loss': current_price * (1 - self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 + self.config.take_profit_pct / 100)
            }
        
        # Death Cross
        elif prev_fast >= prev_slow and sma_fast < sma_slow:
            return {
                'signal': SignalType.SELL,
                'confidence': min((sma_slow - sma_fast) / sma_fast * 10, 1.0),
                'reason': 'Death Cross detectado',
                'price': current_price,
                'stop_loss': current_price * (1 + self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 - self.config.take_profit_pct / 100)
            }
        
        # Seguir tendencia si ya hay cruce
        elif sma_fast > sma_slow and current_price > sma_fast:
            return {
                'signal': SignalType.BUY,
                'confidence': 0.5,
                'reason': 'Tendencia alcista confirmada',
                'price': current_price,
                'stop_loss': current_price * (1 - self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 + self.config.take_profit_pct / 100)
            }
        
        return {
            'signal': SignalType.HOLD,
            'confidence': 0.0,
            'reason': 'Sin cruce de medias',
            'price': current_price,
            'stop_loss': None,
            'take_profit': None
        }


class Bollinger_EA(ExpertAdvisor):
    """Expert Advisor basado en Bandas de Bollinger"""
    
    def _generate_signal(self, data: pd.DataFrame, latest: pd.Series) -> Dict:
        current_price = latest['close']
        bb_lower = latest.get('bb_lower')
        bb_upper = latest.get('bb_upper')
        bb_middle = latest.get('bb_middle')
        
        if any(pd.isna(x) for x in [bb_lower, bb_upper, bb_middle]):
            return {
                'signal': SignalType.HOLD,
                'confidence': 0.0,
                'reason': 'Bandas de Bollinger no disponibles',
                'price': current_price,
                'stop_loss': None,
                'take_profit': None
            }
        
        # Precio toca o cruza banda inferior (compra)
        if current_price <= bb_lower:
            distance = (bb_lower - current_price) / bb_lower
            return {
                'signal': SignalType.BUY,
                'confidence': min(distance * 10, 1.0),
                'reason': f'Precio en banda inferior ({current_price:.2f} <= {bb_lower:.2f})',
                'price': current_price,
                'stop_loss': current_price * (1 - self.config.stop_loss_pct / 100),
                'take_profit': bb_middle  # Target: banda media
            }
        
        # Precio toca o cruza banda superior (venta)
        elif current_price >= bb_upper:
            distance = (current_price - bb_upper) / bb_upper
            return {
                'signal': SignalType.SELL,
                'confidence': min(distance * 10, 1.0),
                'reason': f'Precio en banda superior ({current_price:.2f} >= {bb_upper:.2f})',
                'price': current_price,
                'stop_loss': current_price * (1 + self.config.stop_loss_pct / 100),
                'take_profit': bb_middle  # Target: banda media
            }
        
        return {
            'signal': SignalType.HOLD,
            'confidence': 0.0,
            'reason': 'Precio dentro de las bandas',
            'price': current_price,
            'stop_loss': None,
            'take_profit': None
        }


# Estrategia combinada (ensemble de EAs)
class Ensemble_EA(ExpertAdvisor):
    """
    Expert Advisor que combina múltiples estrategias.
    Usa votación ponderada para generar señales más robustas.
    """
    
    def __init__(self, config: EAConfig):
        super().__init__(config)
        self.sub_eas = [
            RSI_EA(config),
            MACD_EA(config),
            MA_Crossover_EA(config),
            Bollinger_EA(config)
        ]
        self.weights = [0.25, 0.30, 0.25, 0.20]  # Pesos por EA
    
    def _generate_signal(self, data: pd.DataFrame, latest: pd.Series) -> Dict:
        current_price = latest['close']
        
        # Obtener señales de todos los EAs
        signals = []
        for ea in self.sub_eas:
            signal = ea._generate_signal(data, latest)
            signals.append(signal)
        
        # Votación ponderada
        buy_score = 0
        sell_score = 0
        reasons = []
        
        for signal, weight in zip(signals, self.weights):
            if signal['signal'] == SignalType.BUY:
                buy_score += weight * signal['confidence']
                reasons.append(signal['reason'])
            elif signal['signal'] == SignalType.SELL:
                sell_score += weight * signal['confidence']
                reasons.append(signal['reason'])
        
        # Decisión final
        threshold = 0.4  # Umbral para generar señal
        
        if buy_score > threshold and buy_score > sell_score:
            return {
                'signal': SignalType.BUY,
                'confidence': buy_score,
                'reason': 'Consenso alcista: ' + '; '.join(reasons[:2]),
                'price': current_price,
                'stop_loss': current_price * (1 - self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 + self.config.take_profit_pct / 100)
            }
        elif sell_score > threshold and sell_score > buy_score:
            return {
                'signal': SignalType.SELL,
                'confidence': sell_score,
                'reason': 'Consenso bajista: ' + '; '.join(reasons[:2]),
                'price': current_price,
                'stop_loss': current_price * (1 + self.config.stop_loss_pct / 100),
                'take_profit': current_price * (1 - self.config.take_profit_pct / 100)
            }
        
        return {
            'signal': SignalType.HOLD,
            'confidence': 0.0,
            'reason': f'Sin consenso (Buy: {buy_score:.2f}, Sell: {sell_score:.2f})',
            'price': current_price,
            'stop_loss': None,
            'take_profit': None
        }
