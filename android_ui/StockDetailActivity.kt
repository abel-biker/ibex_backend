package com.example.ibex35trading

import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.ibex35trading.api.IBEX35Repository
import com.example.ibex35trading.api.StockScoreResponse
import com.example.ibex35trading.databinding.ActivityStockDetailBinding
import kotlinx.coroutines.launch

class StockDetailActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityStockDetailBinding
    private lateinit var repository: IBEX35Repository
    private lateinit var symbol: String
    
    companion object {
        private const val EXTRA_SYMBOL = "extra_symbol"
        
        fun start(context: Context, symbol: String) {
            val intent = Intent(context, StockDetailActivity::class.java).apply {
                putExtra(EXTRA_SYMBOL, symbol)
            }
            context.startActivity(intent)
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityStockDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        symbol = intent.getStringExtra(EXTRA_SYMBOL) ?: return
        repository = IBEX35Repository()
        
        setupToolbar()
        setupButtons()
        loadStockDetail()
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }
    
    private fun setupButtons() {
        binding.btnFavorite.setOnClickListener {
            toggleFavorite()
        }
        
        binding.btnCreateAlert.setOnClickListener {
            // Implementar creación de alertas
            Toast.makeText(this, "Crear alerta para $symbol", Toast.LENGTH_SHORT).show()
        }
        
        binding.btnViewChart.setOnClickListener {
            // Implementar visualización de gráfico
            Toast.makeText(this, "Ver gráfico de $symbol", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun loadStockDetail() {
        lifecycleScope.launch {
            try {
                val result = repository.getStockScore(symbol)
                
                result.onSuccess { stock ->
                    displayStockData(stock)
                }
                
                result.onFailure { error ->
                    Toast.makeText(
                        this@StockDetailActivity,
                        "Error: ${error.message}",
                        Toast.LENGTH_LONG
                    ).show()
                    finish()
                }
                
            } catch (e: Exception) {
                Toast.makeText(
                    this@StockDetailActivity,
                    "Error de conexión: ${e.message}",
                    Toast.LENGTH_LONG
                ).show()
                finish()
            }
        }
    }
    
    private fun displayStockData(stock: StockScoreResponse) {
        binding.apply {
            // Header
            textDetailName.text = stock.name
            textDetailSymbol.text = "${stock.symbol} • ${stock.sector}"
            
            // Precio
            textDetailPrice.text = "€%.2f".format(stock.price)
            
            // Score y rating
            textDetailScore.text = "%.1f".format(stock.score)
            textDetailRating.text = stock.rating
            
            val scoreColor = getScoreColor(stock.score)
            textDetailScore.setTextColor(scoreColor)
            textDetailRating.setTextColor(scoreColor)
            
            // Señal AI
            chipDetailSignal.text = stock.signal
            chipDetailSignal.setChipBackgroundColorResource(
                when (stock.signal) {
                    "BUY" -> android.R.color.holo_green_light
                    "SELL" -> android.R.color.holo_red_light
                    else -> android.R.color.darker_gray
                }
            )
            
            // Probabilidad ML
            val mlProb = stock.components.ml_prediction.probability
            textDetailProbability.text = "Probabilidad: ${(mlProb * 100).toInt()}%"
            textDetailProbability.setTextColor(scoreColor)
            
            // Razón y confianza
            textDetailReason.text = stock.reason
            textDetailConfidence.text = stock.confidence
            textDetailConfidence.setTextColor(
                when (stock.confidence) {
                    "HIGH" -> Color.parseColor("#4CAF50")
                    "MEDIUM" -> Color.parseColor("#FF9800")
                    "LOW" -> Color.parseColor("#F44336")
                    else -> Color.parseColor("#9E9E9E")
                }
            )
            
            textDetailMethodology.text = "Metodología: ${stock.methodology}"
            
            // Componentes AI
            displayAIComponents(stock)
            
            // Indicadores técnicos
            displayTechnicalIndicators(stock)
        }
    }
    
    private fun displayAIComponents(stock: StockScoreResponse) {
        binding.apply {
            // XGBoost ML
            val mlScore = stock.components.ml_prediction.score
            textMLScore.text = "%.1f".format(mlScore)
            progressML.progress = (mlScore * 10).toInt()
            progressML.setIndicatorColor(getScoreColor(mlScore))
            
            // Prophet
            val prophetScore = stock.components.prophet.score
            val prophetChange = stock.components.prophet.predicted_change_pct
            textProphetScore.text = "%.1f".format(prophetScore)
            progressProphet.progress = (prophetScore * 10).toInt()
            progressProphet.setIndicatorColor(getScoreColor(prophetScore))
            textProphetChange.text = "Predicción: %+.2f%% en 15 días".format(prophetChange)
            
            // Danelfin Técnico
            val techScore = stock.components.technical.score
            textTechnicalScore.text = "%.1f".format(techScore)
            progressTechnical.progress = (techScore * 10).toInt()
            progressTechnical.setIndicatorColor(getScoreColor(techScore))
            
            // FinBERT Sentiment
            val sentScore = stock.components.sentiment.score
            val sentiment = stock.components.sentiment.sentiment
            textSentimentScore.text = "%.1f".format(sentScore)
            progressSentiment.progress = (sentScore * 10).toInt()
            progressSentiment.setIndicatorColor(getScoreColor(sentScore))
            textSentimentStatus.text = "Sentimiento: ${sentiment.capitalize()}"
        }
    }
    
    private fun displayTechnicalIndicators(stock: StockScoreResponse) {
        binding.apply {
            stock.indicators.rsi?.let { 
                textRSI.text = "%.1f".format(it)
            }
            
            stock.indicators.macd?.let { 
                textMACD.text = "%.3f".format(it)
            }
            
            stock.indicators.sma_20?.let { 
                textSMA20.text = "€%.2f".format(it)
            }
            
            stock.indicators.sma_50?.let { 
                textSMA50.text = "€%.2f".format(it)
            }
        }
    }
    
    private fun toggleFavorite() {
        lifecycleScope.launch {
            try {
                val result = repository.addFavorite(symbol)
                result.onSuccess {
                    binding.btnFavorite.setImageResource(R.drawable.ic_star_filled)
                    Toast.makeText(
                        this@StockDetailActivity,
                        "⭐ Añadido a favoritos",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            } catch (e: Exception) {
                Toast.makeText(
                    this@StockDetailActivity,
                    "Error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }
    
    private fun getScoreColor(score: Float): Int {
        return when {
            score >= 8.0 -> Color.parseColor("#4CAF50")
            score >= 6.5 -> Color.parseColor("#8BC34A")
            score >= 5.0 -> Color.parseColor("#FF9800")
            score >= 3.5 -> Color.parseColor("#FF5722")
            else -> Color.parseColor("#F44336")
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
