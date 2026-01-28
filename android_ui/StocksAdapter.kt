package com.example.ibex35trading.adapters

import android.graphics.Color
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.ibex35trading.R
import com.example.ibex35trading.api.StockRanking
import com.example.ibex35trading.databinding.ItemStockBinding

class StocksAdapter(
    private val onItemClick: (StockRanking) -> Unit,
    private val onFavoriteClick: (StockRanking) -> Unit
) : ListAdapter<StockRanking, StocksAdapter.StockViewHolder>(StockDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): StockViewHolder {
        val binding = ItemStockBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return StockViewHolder(binding, onItemClick, onFavoriteClick)
    }
    
    override fun onBindViewHolder(holder: StockViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    class StockViewHolder(
        private val binding: ItemStockBinding,
        private val onItemClick: (StockRanking) -> Unit,
        private val onFavoriteClick: (StockRanking) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(stock: StockRanking) {
            binding.apply {
                // Nombre y símbolo
                textStockName.text = stock.name
                textStockSymbol.text = "${stock.symbol} • ${stock.sector}"
                
                // Precio
                textPrice.text = "€%.2f".format(stock.price)
                textPriceChange.text = if (stock.change_pct >= 0) {
                    "+%.2f%%".format(stock.change_pct)
                } else {
                    "%.2f%%".format(stock.change_pct)
                }
                
                // Color del cambio
                val changeColor = if (stock.change_pct >= 0) {
                    Color.parseColor("#4CAF50")
                } else {
                    Color.parseColor("#F44336")
                }
                textPriceChange.setTextColor(changeColor)
                
                // Score y rating
                textScore.text = "%.1f".format(stock.score)
                textRating.text = stock.rating
                
                // Color del score
                val scoreColor = getScoreColor(stock.score)
                textScore.setTextColor(scoreColor)
                textRating.setTextColor(scoreColor)
                
                // Señal AI (si está disponible)
                if (stock.signal != null) {
                    chipSignal.text = stock.signal
                    chipSignal.setChipBackgroundColorResource(
                        when (stock.signal) {
                            "BUY" -> android.R.color.holo_green_light
                            "SELL" -> android.R.color.holo_red_light
                            else -> android.R.color.darker_gray
                        }
                    )
                    
                    // Probabilidad
                    if (stock.ml_probability != null) {
                        textProbability.text = "${(stock.ml_probability * 100).toInt()}%"
                        textProbability.setTextColor(scoreColor)
                    }
                }
                
                // Confianza
                textConfidence.text = stock.confidence
                textConfidence.setTextColor(
                    when (stock.confidence) {
                        "HIGH" -> Color.parseColor("#4CAF50")
                        "MEDIUM" -> Color.parseColor("#FF9800")
                        "LOW" -> Color.parseColor("#F44336")
                        else -> Color.parseColor("#9E9E9E")
                    }
                )
                
                // Progress de confianza
                val confidencePercent = when (stock.confidence) {
                    "HIGH" -> 85
                    "MEDIUM" -> 50
                    "LOW" -> 25
                    else -> 0
                }
                progressConfidence.progress = confidencePercent
                
                // Razón y metodología
                if (stock.reason != null) {
                    textReason.text = stock.reason
                }
                
                if (stock.methodology != null) {
                    textMethodology.text = stock.methodology
                }
                
                // Click listeners
                root.setOnClickListener { onItemClick(stock) }
                iconFavorite.setOnClickListener { onFavoriteClick(stock) }
            }
        }
        
        private fun getScoreColor(score: Float): Int {
            return when {
                score >= 8.0 -> Color.parseColor("#4CAF50") // Verde fuerte
                score >= 6.5 -> Color.parseColor("#8BC34A") // Verde claro
                score >= 5.0 -> Color.parseColor("#FF9800") // Naranja
                score >= 3.5 -> Color.parseColor("#FF5722") // Naranja oscuro
                else -> Color.parseColor("#F44336") // Rojo
            }
        }
    }
    
    class StockDiffCallback : DiffUtil.ItemCallback<StockRanking>() {
        override fun areItemsTheSame(oldItem: StockRanking, newItem: StockRanking): Boolean {
            return oldItem.symbol == newItem.symbol
        }
        
        override fun areContentsTheSame(oldItem: StockRanking, newItem: StockRanking): Boolean {
            return oldItem == newItem
        }
    }
}

// Extensión de StockRanking para incluir datos de IA
val StockRanking.signal: String?
    get() = null // Se debe añadir al data class original

val StockRanking.ml_probability: Float?
    get() = null // Se debe añadir al data class original

val StockRanking.reason: String?
    get() = null // Se debe añadir al data class original

val StockRanking.methodology: String?
    get() = null // Se debe añadir al data class original
