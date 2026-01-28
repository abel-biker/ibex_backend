package com.example.ibex35trading

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.ibex35trading.adapters.StocksAdapter
import com.example.ibex35trading.api.IBEX35Repository
import com.example.ibex35trading.databinding.ActivityMainBinding
import com.google.android.material.chip.Chip
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var repository: IBEX35Repository
    private lateinit var adapter: StocksAdapter
    
    private var currentSector: String? = null
    private var isLoading = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        repository = IBEX35Repository()
        setupRecyclerView()
        setupChips()
        setupFab()
        
        // Cargar ranking inicial
        loadRanking()
    }
    
    private fun setupRecyclerView() {
        adapter = StocksAdapter(
            onItemClick = { stock ->
                // Abrir detalle de la acción
                StockDetailActivity.start(this, stock.symbol)
            },
            onFavoriteClick = { stock ->
                toggleFavorite(stock.symbol)
            }
        )
        
        binding.recyclerViewStocks.apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = this@MainActivity.adapter
        }
    }
    
    private fun setupChips() {
        binding.chipGroupSectors.setOnCheckedStateChangeListener { group, checkedIds ->
            if (checkedIds.isEmpty()) return@setOnCheckedStateChangeListener
            
            val chip = findViewById<Chip>(checkedIds.first())
            currentSector = when (chip.id) {
                binding.chipFinanciero.id -> "Financiero"
                binding.chipEnergia.id -> "Energía"
                binding.chipTelecomunicaciones.id -> "Telecomunicaciones"
                else -> null
            }
            
            loadRanking()
        }
    }
    
    private fun setupFab() {
        binding.fabRefresh.setOnClickListener {
            loadRanking(forceRefresh = true)
        }
    }
    
    private fun loadRanking(forceRefresh: Boolean = false) {
        if (isLoading) return
        
        isLoading = true
        showLoading(true)
        
        lifecycleScope.launch {
            try {
                val result = repository.getRanking(
                    limit = 35,
                    sector = currentSector,
                    minScore = null
                )
                
                result.onSuccess { response ->
                    adapter.submitList(response.ranking)
                    showLoading(false)
                    
                    if (forceRefresh) {
                        Toast.makeText(
                            this@MainActivity,
                            "✅ Datos actualizados",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }
                
                result.onFailure { error ->
                    showLoading(false)
                    Toast.makeText(
                        this@MainActivity,
                        "Error: ${error.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
                
            } catch (e: Exception) {
                showLoading(false)
                Toast.makeText(
                    this@MainActivity,
                    "Error de conexión: ${e.message}",
                    Toast.LENGTH_LONG
                ).show()
            } finally {
                isLoading = false
            }
        }
    }
    
    private fun toggleFavorite(symbol: String) {
        lifecycleScope.launch {
            try {
                // Implementar lógica de favoritos
                val result = repository.addFavorite(symbol)
                result.onSuccess {
                    Toast.makeText(
                        this@MainActivity,
                        "⭐ Añadido a favoritos",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            } catch (e: Exception) {
                Toast.makeText(
                    this@MainActivity,
                    "Error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }
    
    private fun showLoading(show: Boolean) {
        // Implementar indicador de carga
        binding.fabRefresh.isEnabled = !show
    }
}
