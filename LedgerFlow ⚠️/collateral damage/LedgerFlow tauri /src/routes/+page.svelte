<script lang="ts">
  import { page } from '$app/stores';
  import { simulationConfig, simulationStats, sampleInvoice, runSimulation, updateConfig, simulationError, isSimulating } from '$lib/simulation_store';
  import { runSimulation as runSimulationDebug, simulationResult, simulationError as debugError, isLoading } from '$lib/stores/simulation';
  import type { SimulationConfig } from '$lib/types';
  import { onMount } from 'svelte';
  import Toast from '$lib/components/Toast.svelte';
  import type { Invoice, InvoiceItem, TaxEntry } from '$lib/types';

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'grid_view' },
    { id: 'simulator', label: 'Simulator', icon: 'play_circle' },
    { id: 'settings', label: 'Settings', icon: 'settings' }
  ];

  let currentPage = 'simulator';
  let selectedInvoiceType = 'gst';
  let totalRevenue = 500000;
  let startDate = '';
  let endDate = '';
  let minItemsPerInvoice = 1;
  let maxItemsPerInvoice = 5;
  let minAmountPerInvoice = 1000;
  let maxAmountPerInvoice = 50000;
  let useSelectedItems = false;
  let mostSoldItems: string[] = [];
  let leastSoldItems: string[] = [];
  let useSeedValue = false;
  let seedValue = 12345;
  let customerDistribution: SimulationConfig['realism_mode'] = 'random';
  let previewType = 'random';
  let hasRunSimulation = false;
  let showAdvancedOptions = false;
  let lastSavedTime = 'Never';
  let showTaxSelector = true;
  let selectedTaxTemplate: 'gst' | 'vat' | 'plain' = 'gst';
  let realityBuffer = 0;
  let distributionMode: 'even' | 'weighted' | 'burst' = 'even';
  let customerRepeatRate = 0;

  // Enhanced catalog items for demonstration
  const catalogItems = [
    { id: 'item1', name: 'Dell Latitude 5520 Laptop', price: 45000, category: 'Electronics' },
    { id: 'item2', name: 'Herman Miller Aeron Chair', price: 85000, category: 'Furniture' },
    { id: 'item3', name: 'HP LaserJet Pro M404n', price: 12000, category: 'Electronics' },
    { id: 'item4', name: 'Steelcase Series 7 Desk', price: 150000, category: 'Furniture' },
    { id: 'item5', name: 'Microsoft 365 Business Premium', price: 5000, category: 'Software' },
    { id: 'item6', name: 'Enterprise Internet Service', price: 20000, category: 'Services' },
    { id: 'item7', name: 'Cisco IP Phone 8845', price: 80000, category: 'Electronics' },
    { id: 'item8', name: 'Filing Cabinet 4-Drawer', price: 60000, category: 'Furniture' },
    { id: 'item9', name: 'Adobe Creative Suite', price: 25000, category: 'Software' },
    { id: 'item10', name: 'Security Camera System', price: 35000, category: 'Electronics' }
  ];

  let toastMessage = '';
  let toastType: 'error' | 'success' | 'warning' = 'error';

  // Connect UI state to simulation config store
  $: {
    // Only update if we have valid dates to avoid sending empty values
    if (startDate && endDate) {
      console.log('🔗 UI binding update:', {
        revenue_target: totalRevenue,
        start_date: startDate,
        end_date: endDate,
        min_items: minItemsPerInvoice,
        max_items: maxItemsPerInvoice,
        min_invoice_amount: minAmountPerInvoice,
        max_invoice_amount: maxAmountPerInvoice,
        invoice_count_mode: invoiceCountMode,
        manual_invoice_count: manualInvoiceCount,
        reality_buffer: realityBuffer
      });
      
      updateConfig({
        invoice_type: selectedTaxTemplate,
        revenue_target: totalRevenue,
        start_date: startDate,
        end_date: endDate,
        min_items: minItemsPerInvoice,
        max_items: maxItemsPerInvoice,
        min_invoice_amount: minAmountPerInvoice,
        max_invoice_amount: maxAmountPerInvoice,
        item_filter_mode: useSelectedItems ? 'selected' : 'all',
        selected_items: useSelectedItems ? mostSoldItems.concat(leastSoldItems) : [],
        name_type: 'indian_company',
        realism_mode: customerDistribution,
        seed: useSeedValue ? seedValue : undefined,
        invoice_count_mode: invoiceCountMode,
        manual_invoice_count: manualInvoiceCount,
        reality_buffer: realityBuffer,
        distribution_mode: distributionMode,
        customer_repeat_rate: customerRepeatRate
      });
    }
  }

  // Initialize with default dates if not set
  onMount(() => {
    const today = new Date();
    const thirtyDaysFromNow = new Date();
    thirtyDaysFromNow.setDate(today.getDate() + 30);
    
    startDate = today.toISOString().split('T')[0];
    endDate = thirtyDaysFromNow.toISOString().split('T')[0];
  });

  // Handle run simulation button click
  async function handleRunSimulation() {
    try {
      await runSimulation();
      hasRunSimulation = true;
      lastSavedTime = 'Just now';
      toastMessage = 'Simulation completed successfully';
      toastType = 'success';
    } catch (error) {
      console.error('Simulation failed');
      toastMessage = $simulationError || 'Simulation failed';
      toastType = 'error';
    }
  }

  function handleToastClose() {
    toastMessage = '';
  }

  function handleSaveConfiguration() {
    console.log('Configuration saved');
    lastSavedTime = 'Just now';
    toastMessage = 'Configuration saved successfully';
    toastType = 'success';
  }

  function handleCancel() {
    totalRevenue = 500000;
    minItemsPerInvoice = 1;
    maxItemsPerInvoice = 5;
    minAmountPerInvoice = 1000;
    maxAmountPerInvoice = 50000;
  }

  // Get invoice type color
  function getInvoiceTypeColor(type: string) {
    switch (type.toLowerCase()) {
      case 'gst': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'vat': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  }

  // Get invoice type label
  function getInvoiceTypeLabel(type: string) {
    switch (type.toLowerCase()) {
      case 'gst': return 'GST';
      case 'vat': return 'VAT';
      default: return 'Standard';
    }
  }

  // Format currency
  function formatCurrency(amount: number) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  function handleTaxTemplateSelect(template: 'gst' | 'vat' | 'plain') {
    selectedTaxTemplate = template;
    showTaxSelector = false;
    selectedInvoiceType = template;
  }

  // Only show tax selector if on Simulator page
  $: showTaxSelectorOnSimulator = showTaxSelector && currentPage === 'simulator';

  // Invoice count control
  let invoiceCountMode: 'auto' | 'manual' = 'auto';
  let manualInvoiceCount: number = 50;

  // Tax rates for GST/VAT
  let gstRates = [5, 12, 18, 28];
  let vatRates = [0, 10];

  function calculateSubtotal(items: InvoiceItem[]): number {
    return items.reduce((sum: number, item: InvoiceItem) => sum + (item.total || item.amount), 0);
  }

  // Debug function
  async function testSimulation() {
    const testConfig: SimulationConfig = {
      revenue_target: 500000,
      start_date: '2023-01-01',
      end_date: '2023-12-31',
      invoice_type: 'gst',
      min_items: 1,
      max_items: 10,
      min_invoice_amount: 1000,
      max_invoice_amount: 50000,
      item_filter_mode: 'all',
      selected_items: [],
      name_type: 'indian_company',
      realism_mode: 'pareto'
    };
    
    console.log('Testing simulation with config:', testConfig);
    await runSimulationDebug(testConfig);
  }
</script>

<div class="relative h-screen bg-slate-50 font-inter">
  <!-- Sidebar -->
  <aside class="fixed left-0 top-0 w-64 h-screen bg-slate-900 text-white flex flex-col shadow-xl z-20">
    <div class="px-6 py-5 border-b border-slate-700/50">
      <h1 class="text-lg font-bold tracking-tight">LedgerFlow</h1>
      <p class="text-xs text-slate-400 mt-1">Enterprise Simulation Engine</p>
    </div>
    
    <nav class="flex-1 px-3 py-4">
      {#each navItems as item}
        <button
          class="w-full flex items-center gap-3 px-4 py-3 rounded-md text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all {currentPage === item.id ? 'bg-slate-800 text-white shadow-sm' : ''}"
          on:click={() => currentPage = item.id}
        >
          <span class="material-symbols-rounded text-xl">{item.icon}</span>
          <span class="text-sm font-medium">{item.label}</span>
        </button>
      {/each}
    </nav>

    <div class="p-4 border-t border-slate-700/50">
      <div class="flex items-center gap-3 px-2">
        <div class="w-8 h-8 rounded bg-slate-700 flex items-center justify-center">
          <span class="material-symbols-rounded text-lg">account_circle</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">Professional Edition</p>
          <p class="text-xs text-slate-400">v2.1.0</p>
        </div>
      </div>
    </div>
  </aside>

  <!-- Main content wrapper -->
  <div class="ml-64 h-screen flex flex-col">
    <!-- Header -->
    <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 shadow-sm">
      <div class="flex items-center gap-4">
        <h2 class="text-lg font-semibold text-slate-900">Simulation Configuration</h2>
        <div class="h-5 w-px bg-slate-200"></div>
        <span class="px-3 py-1 rounded-full text-sm font-medium border {getInvoiceTypeColor(selectedInvoiceType)}">
          {getInvoiceTypeLabel(selectedInvoiceType)}
        </span>
      </div>
      <div class="flex items-center gap-3">
        <button class="inline-flex items-center px-4 py-2 bg-white border border-slate-200 rounded-md shadow-sm text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
          <span class="material-symbols-rounded text-lg mr-2">upload_file</span>
          Import Data
        </button>
        <button 
          class="inline-flex items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          on:click={handleSaveConfiguration}
        >
          <span class="material-symbols-rounded text-lg mr-2">save</span>
          Save Configuration
        </button>
      </div>
    </header>

    <!-- Main scrollable area -->
    <main class="flex-1 overflow-y-auto">
      <div class="flex gap-6 p-6 h-full">
        <!-- Left Column: Simulation Parameters (40%) -->
        <div class="w-2/5 space-y-6">
          <!-- Revenue & Time Settings -->
          <div class="bg-white rounded-lg border border-slate-200 shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200">
              <h3 class="text-base font-semibold text-slate-900">Revenue & Time</h3>
            </div>
            <div class="p-6 space-y-6">
              <div>
                <label for="revenue" class="block text-sm font-medium text-slate-700 mb-2">Total Revenue Target (₹)</label>
                <input id="revenue" type="number" bind:value={totalRevenue} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" />
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="start-date" class="block text-sm font-medium text-slate-700 mb-2">Start Date</label>
                  <input id="start-date" type="date" bind:value={startDate} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" />
                </div>
                <div>
                  <label for="end-date" class="block text-sm font-medium text-slate-700 mb-2">End Date</label>
                  <input id="end-date" type="date" bind:value={endDate} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" />
                </div>
              </div>
            </div>
          </div>

          <!-- Invoice Bounds -->
          <div class="bg-white rounded-lg border border-slate-200 shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <h3 class="text-base font-semibold text-slate-900">Invoice Bounds</h3>
              <div class="flex items-center gap-2">
                <label class="text-xs font-medium text-slate-600 flex items-center gap-1">
                  <input type="radio" bind:group={invoiceCountMode} value="auto" class="mr-1" /> Auto
                </label>
                <label class="text-xs font-medium text-slate-600 flex items-center gap-1">
                  <input type="radio" bind:group={invoiceCountMode} value="manual" class="mr-1" /> Manual
                </label>
              </div>
            </div>
            <div class="p-6 space-y-6">
              {#if invoiceCountMode === 'manual'}
                <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
                  <label for="invoice-count" class="block text-sm font-medium text-blue-800 mb-2">Number of Invoices</label>
                  <input id="invoice-count" type="number" bind:value={manualInvoiceCount} min="1" max="100" class="w-full h-10 px-3 py-2 bg-white border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" />
                  <p class="text-xs text-blue-600 mt-1">Generate exactly this many invoices (revenue will be distributed across them)</p>
                </div>
              {:else}
                <div class="bg-green-50 border border-green-200 rounded-md p-4">
                  <p class="text-sm text-green-800">Auto mode: Invoice count will be calculated automatically based on your revenue target and invoice amount ranges.</p>
                </div>
              {/if}
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="min-items" class="block text-sm font-medium text-slate-700 mb-2">Min Items/Invoice</label>
                  <input id="min-items" type="number" bind:value={minItemsPerInvoice} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" />
                </div>
                <div>
                  <label for="max-items" class="block text-sm font-medium text-slate-700 mb-2">Max Items/Invoice</label>
                  <input id="max-items" type="number" bind:value={maxItemsPerInvoice} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="min-amount" class="block text-sm font-medium text-slate-700 mb-2">Min Invoice Amount (₹)</label>
                  <input id="min-amount" type="number" bind:value={minAmountPerInvoice} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" />
                </div>
                <div>
                  <label for="max-amount" class="block text-sm font-medium text-slate-700 mb-2">Max Invoice Amount (₹)</label>
                  <input id="max-amount" type="number" bind:value={maxAmountPerInvoice} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" />
                </div>
              </div>
              <div class="bg-slate-50 border border-slate-200 rounded-md p-3">
                <p class="text-xs text-slate-600">
                  <strong>Current Configuration:</strong> 
                  {#if invoiceCountMode === 'manual'}
                    Generate {manualInvoiceCount} invoices, each between ₹{minAmountPerInvoice.toLocaleString()} - ₹{maxAmountPerInvoice.toLocaleString()}, targeting ₹{totalRevenue.toLocaleString()} total revenue.
                  {:else}
                    Generate invoices automatically to reach ₹{totalRevenue.toLocaleString()} revenue, each between ₹{minAmountPerInvoice.toLocaleString()} - ₹{maxAmountPerInvoice.toLocaleString()}.
                  {/if}
                  Items per invoice: {minItemsPerInvoice}-{maxItemsPerInvoice}.
                </p>
              </div>
            </div>
          </div>

          <!-- Item Selection Rules -->
          <div class="bg-white rounded-lg border border-slate-200 shadow-sm">
            <div class="px-6 py-4 border-b border-slate-200">
              <h3 class="text-base font-semibold text-slate-900">Item Selection Rules</h3>
            </div>
            <div class="p-6 space-y-6">
              <!-- Filter Type -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-3">Filter Type</label>
                <div class="space-y-3">
                  <label class="flex items-center">
                    <input type="radio" bind:group={useSelectedItems} value={false} class="mr-3">
                    <span class="text-sm text-slate-700">Use All Items</span>
                  </label>
                  <label class="flex items-center">
                    <input type="radio" bind:group={useSelectedItems} value={true} class="mr-3">
                    <span class="text-sm text-slate-700">Use Selected Items</span>
                  </label>
                </div>
              </div>

              {#if useSelectedItems}
                <!-- Item Selection -->
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-slate-700 mb-2">Items to Include</label>
                    <div class="max-h-32 overflow-y-auto border border-slate-200 rounded-md">
                      {#each catalogItems as item}
                        <label class="flex items-center px-3 py-2 hover:bg-slate-50 cursor-pointer">
                          <input type="checkbox" class="mr-3">
                          <div class="flex-1">
                            <div class="text-sm text-slate-700">{item.name}</div>
                            <div class="text-xs text-slate-500">{formatCurrency(item.price)}</div>
                          </div>
                        </label>
                      {/each}
                    </div>
                  </div>
                </div>
              {/if}
            </div>
          </div>

          <!-- Tax Template Details (conditional) -->
          {#if selectedTaxTemplate === 'gst'}
            <div class="bg-white rounded-lg border border-slate-200 shadow-sm">
              <div class="px-6 py-4 border-b border-slate-200">
                <h3 class="text-base font-semibold text-slate-900">GST Details</h3>
              </div>
              <div class="p-6">
                <label class="block text-sm font-medium text-slate-700 mb-2">Allowed GST Rates (%)</label>
                <div class="flex gap-3 flex-wrap">
                  {#each gstRates as rate}
                    <span class="inline-block px-3 py-1 rounded bg-emerald-100 text-emerald-800 font-semibold">{rate}%</span>
                  {/each}
                </div>
              </div>
            </div>
          {:else if selectedTaxTemplate === 'vat'}
            <div class="bg-white rounded-lg border border-slate-200 shadow-sm">
              <div class="px-6 py-4 border-b border-slate-200">
                <h3 class="text-base font-semibold text-slate-900">VAT Details</h3>
              </div>
              <div class="p-6">
                <label class="block text-sm font-medium text-slate-700 mb-2">Allowed VAT Rates (%)</label>
                <div class="flex gap-3 flex-wrap">
                  {#each vatRates as rate}
                    <span class="inline-block px-3 py-1 rounded bg-purple-100 text-purple-800 font-semibold">{rate}%</span>
                  {/each}
                </div>
              </div>
            </div>
          {/if}

          <!-- Advanced Settings (collapsible) -->
          <div class="bg-white rounded-lg border border-slate-200 shadow-sm">
            <button class="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-slate-50 transition-colors" on:click={() => showAdvancedOptions = !showAdvancedOptions}>
              <h3 class="text-base font-semibold text-slate-900">Advanced Settings</h3>
              <span class="material-symbols-rounded text-slate-400 transition-transform" class:rotate-180={showAdvancedOptions}>expand_more</span>
            </button>
            {#if showAdvancedOptions}
              <div class="px-6 pb-6 space-y-6">
                <!-- Reality Buffer -->
                <div>
                  <label for="reality-buffer" class="block text-sm font-medium text-slate-700 mb-2">Reality Buffer (%)</label>
                  <input id="reality-buffer" type="range" min="0" max="50" step="5" bind:value={realityBuffer} class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer" />
                  <div class="flex justify-between text-xs text-slate-500 mt-1">
                    <span>0% (Exact)</span>
                    <span class="font-medium text-slate-700">{realityBuffer}%</span>
                    <span>50% (High Variation)</span>
                  </div>
                  <p class="text-xs text-slate-500 mt-2">Adds realistic variation to invoice amounts and timing</p>
                </div>

                <!-- Distribution Mode -->
                <div>
                  <label for="distribution-mode" class="block text-sm font-medium text-slate-700 mb-2">Invoice Distribution</label>
                  <select id="distribution-mode" bind:value={distributionMode} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
                    <option value="even">Even Distribution</option>
                    <option value="weighted">End-Loaded (More toward end)</option>
                    <option value="burst">Front-Loaded (Burst at start)</option>
                  </select>
                  <p class="text-xs text-slate-500 mt-1">How invoices are distributed over the time period</p>
                </div>

                <!-- Customer Repeat Rate -->
                <div>
                  <label for="customer-repeat" class="block text-sm font-medium text-slate-700 mb-2">Customer Repeat Rate (%)</label>
                  <input id="customer-repeat" type="range" min="0" max="80" step="10" bind:value={customerRepeatRate} class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer" />
                  <div class="flex justify-between text-xs text-slate-500 mt-1">
                    <span>0% (All New)</span>
                    <span class="font-medium text-slate-700">{customerRepeatRate}%</span>
                    <span>80% (Many Repeats)</span>
                  </div>
                  <p class="text-xs text-slate-500 mt-2">Chance that customers appear in multiple invoices</p>
                </div>

                <!-- Realism Mode -->
                <div>
                  <label for="realism-mode" class="block text-sm font-medium text-slate-700 mb-2">Realism Mode</label>
                  <select id="realism-mode" bind:value={customerDistribution} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
                    <option value="random">Random Distribution</option>
                    <option value="pareto">Pareto Distribution (80/20 rule)</option>
                    <option value="equal">Equal Distribution</option>
                  </select>
                  <p class="text-xs text-slate-500 mt-1">How revenue is distributed across customers</p>
                </div>

                <!-- Use Seed Value -->
                <div>
                  <label class="flex items-center">
                    <input type="checkbox" bind:checked={useSeedValue} class="mr-3">
                    <span class="text-sm font-medium text-slate-700">Use Seed Value for Reproducible Results</span>
                  </label>
                  {#if useSeedValue}
                    <input type="number" bind:value={seedValue} class="mt-2 w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors" placeholder="12345" />
                  {/if}
                </div>
                <!-- Preview Sample Mode -->
                <div>
                  <label for="preview-mode" class="block text-sm font-medium text-slate-700 mb-2">Preview Sample Mode</label>
                  <select id="preview-mode" bind:value={previewType} class="w-full h-10 px-3 py-2 bg-white border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
                    <option value="random">Random Sample</option>
                    <option value="min">Minimum Value</option>
                    <option value="max">Maximum Value</option>
                  </select>
                </div>
              </div>
            {/if}
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3">
            <button 
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              on:click={handleSaveConfiguration}
            >
              Save Configuration
            </button>
            <button 
              class="flex-1 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-md font-medium hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              on:click={handleCancel}
            >
              Reset
            </button>
          </div>
        </div>

        <!-- Right Column: Invoice Preview and Stats (60%) -->
        <div class="w-3/5 space-y-6">
          <!-- Invoice Preview -->
          <div class="bg-white rounded-2xl border-2 border-blue-200 shadow-lg p-8">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-2xl font-extrabold text-blue-900 flex items-center gap-2">
                <span class="material-symbols-rounded text-3xl text-blue-500">description</span>
                Invoice Preview
              </h3>
              <div class="flex items-center gap-2">
                <button 
                  class="p-2 hover:bg-blue-50 rounded-full transition-colors"
                  on:click={handleRunSimulation}
                  disabled={$isSimulating}
                >
                  <span class="material-symbols-rounded text-blue-400 hover:text-blue-600">refresh</span>
                </button>
              </div>
            </div>
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-8 shadow-inner">
              {#if $isSimulating}
                <div class="flex items-center justify-center h-48">
                  <div class="text-center">
                    <div class="animate-spin mb-4">
                      <span class="material-symbols-rounded text-4xl text-blue-500">sync</span>
                    </div>
                    <p class="text-lg text-slate-600">Generating invoices...</p>
                    <p class="text-base text-slate-400">This may take a moment</p>
                  </div>
                </div>
              {:else if $simulationError}
                <div class="flex flex-col items-center justify-center h-48">
                  <div class="text-center mb-4">
                    <span class="material-symbols-rounded text-4xl text-rose-500 mb-2">error</span>
                    <p class="text-lg text-rose-600">Simulation Error</p>
                    <p class="text-base text-slate-600 mb-4">{$simulationError}</p>
                    <button 
                      class="px-4 py-2 bg-rose-100 text-rose-700 rounded-md hover:bg-rose-200 transition-colors"
                      on:click={handleRunSimulation}
                    >
                      <span class="material-symbols-rounded text-base mr-1 align-middle">refresh</span>
                      Retry Simulation
                    </button>
                  </div>
                </div>
              {:else if $sampleInvoice}
                <!-- Invoice Header -->
                <div class="flex justify-between items-start mb-8">
                  <div>
                    <h4 class="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">INVOICE</h4>
                    <p class="text-base text-slate-500 font-semibold">#{$sampleInvoice.invoice_number}</p>
                  </div>
                  <div class="text-right">
                    <div class="text-sm font-bold text-slate-700">Date Issued:</div>
                    <div class="text-sm text-slate-600">{new Date($sampleInvoice.date).toLocaleDateString()}</div>
                    <div class="text-sm text-slate-600 mt-1">Due: {new Date(new Date($sampleInvoice.date).getTime() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString()}</div>
                  </div>
                </div>
                <div class="border-t border-slate-200 my-6"></div>
                <!-- Customer Information -->
                <div class="mb-8">
                  <div class="text-sm font-bold text-slate-700 mb-1">Bill To:</div>
                  <div class="text-lg text-slate-700 font-semibold">{$sampleInvoice.customer.name}</div>
                </div>
                <div class="border-t border-slate-200 my-6"></div>
                <!-- Items Table -->
                <div class="mb-8">
                  <div class="grid grid-cols-12 gap-2 text-sm font-bold text-slate-700 pb-3 border-b border-slate-200">
                    <div class="col-span-6">Item</div>
                    <div class="col-span-2 text-right">Qty</div>
                    <div class="col-span-2 text-right">Rate</div>
                    <div class="col-span-2 text-right">Amount</div>
                  </div>
                  {#each $sampleInvoice.items as item}
                    <div class="grid grid-cols-12 gap-2 text-sm text-slate-600 py-3 border-b border-slate-100">
                      <div class="col-span-6 truncate">{item.name || item.item || 'Unknown Item'}</div>
                      <div class="col-span-2 text-right">{item.quantity || item.qty || 1}</div>
                      <div class="col-span-2 text-right">₹{item.rate.toFixed(2)}</div>
                      <div class="col-span-2 text-right">₹{item.amount.toFixed(2)}</div>
                    </div>
                  {/each}
                </div>
                <div class="border-t border-slate-200 my-6"></div>
                <!-- Totals -->
                <div class="flex flex-col items-end gap-2 mb-4">
                  <div class="w-80 max-w-full">
                    <div class="flex justify-between mb-2 text-base text-slate-600">
                      <div>Subtotal:</div>
                      <div>₹{calculateSubtotal($sampleInvoice.items).toFixed(2)}</div>
                    </div>
                    {#if $sampleInvoice.invoice_type !== 'Plain'}
                      <!-- Tax breakdown would go here for GST/VAT invoices -->
                      <div class="flex justify-between mb-2 text-base text-slate-600">
                        <div class="flex items-center gap-1">
                          <span>Tax</span>
                        </div>
                        <div>₹{($sampleInvoice.total - $sampleInvoice.subtotal).toFixed(2)}</div>
                      </div>
                    {/if}
                    <div class="flex justify-between pt-3 border-t border-slate-200 font-extrabold text-2xl text-blue-900 mt-3">
                      <div>Total:</div>
                      <div>₹{$sampleInvoice.total.toFixed(2)}</div>
                    </div>
                  </div>
                </div>
                <div class="border-t border-slate-200 my-6"></div>
                <!-- Payment Terms -->
                <div class="mt-2 text-base text-slate-500 text-center">
                  Payment Terms: Net 30 days<br>
                  Please include invoice number with payment
                </div>
              {:else}
                <div class="flex items-center justify-center h-48 text-slate-400">
                  <div class="text-center">
                    <span class="material-symbols-rounded text-4xl mb-2">description</span>
                    <p class="text-lg">No invoices generated yet</p>
                    <p class="text-base">Configure parameters and run simulation to preview</p>
                    <button 
                      class="mt-4 px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                      on:click={handleRunSimulation}
                    >
                      <span class="material-symbols-rounded text-base mr-1 align-middle">play_circle</span>
                      Run Simulation
                    </button>
                  </div>
                </div>
              {/if}
            </div>
          </div>

          <!-- Statistics Panel -->
          {#if $simulationStats}
            <div class="bg-white rounded-lg border border-slate-200 shadow-sm">
              <div class="px-6 py-4 border-b border-slate-200">
                <h3 class="text-base font-semibold text-slate-900">Simulation Results</h3>
              </div>
              <div class="p-6">
                <div class="grid grid-cols-2 gap-6">
                  <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">{$simulationStats.totalInvoices}</div>
                    <div class="text-sm text-slate-500">Total Invoices</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-green-600">₹{$simulationStats.totalRevenue.toLocaleString()}</div>
                    <div class="text-sm text-slate-500">Total Revenue</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600">₹{Math.round($simulationStats.averageInvoiceValue).toLocaleString()}</div>
                    <div class="text-sm text-slate-500">Avg Invoice Value</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-orange-600">{$simulationStats.uniqueCustomers}</div>
                    <div class="text-sm text-slate-500">Unique Customers</div>
                  </div>
                </div>
              </div>
            </div>
          {:else}
            <!-- Default stats panel when no simulation has run -->
            <div class="bg-white rounded-lg border border-slate-200 shadow-sm">
              <div class="px-6 py-4 border-b border-slate-200">
                <h3 class="text-base font-semibold text-slate-900">Simulation Results</h3>
              </div>
              <div class="p-6">
                <div class="grid grid-cols-2 gap-6">
                  <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">1</div>
                    <div class="text-sm text-slate-500">Total Invoices</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-green-600">₹2,360</div>
                    <div class="text-sm text-slate-500">Total Revenue</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600">₹2,360</div>
                    <div class="text-sm text-slate-500">Avg Invoice Value</div>
                  </div>
                  <div class="text-center">
                    <div class="text-sm text-slate-500">Unique Customers</div>
                  </div>
                </div>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 shadow-sm shrink-0">
      <div class="px-6 py-3 flex items-center justify-between">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full" class:bg-emerald-500={!$isSimulating} class:bg-amber-500={$isSimulating}></div>
            <span class="text-sm text-slate-600">{$isSimulating ? 'Simulating...' : 'System Ready'}</span>
          </div>
          <div class="text-sm text-slate-500">Last saved: {lastSavedTime}</div>
          {#if $simulationError}
            <div class="text-sm text-rose-600 flex items-center gap-1">
              <span class="material-symbols-rounded text-base">error</span>
              {$simulationError}
            </div>
          {/if}
          {#if $debugError}
            <div class="text-sm text-orange-600 flex items-center gap-1">
              <span class="material-symbols-rounded text-base">warning</span>
              Debug: {$debugError}
            </div>
          {/if}
        </div>
        <div class="flex gap-2">
          <button 
            class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-md font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            on:click={testSimulation}
            disabled={$isLoading}
          >
            {#if $isLoading}
              <div class="animate-spin mr-2">
                <span class="material-symbols-rounded text-lg">sync</span>
              </div>
              Testing...
            {:else}
              <span class="material-symbols-rounded text-lg mr-2">bug_report</span>
              Debug Test
            {/if}
          </button>
          
          <button 
            class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            on:click={handleRunSimulation}
            disabled={$isSimulating}
          >
            {#if $isSimulating}
              <div class="animate-spin mr-2">
                <span class="material-symbols-rounded text-lg">sync</span>
              </div>
              Simulating...
            {:else}
              <span class="material-symbols-rounded text-lg mr-2">play_circle</span>
              Run Simulation
            {/if}
          </button>
        </div>
      </div>
    </footer>
  </div>
</div>

{#if showTaxSelectorOnSimulator}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80">
    <div class="bg-white rounded-2xl shadow-2xl p-12 w-full max-w-lg flex flex-col items-center gap-8">
      <h2 class="text-2xl font-extrabold text-slate-900 mb-2">Select Tax Template</h2>
      <p class="text-slate-600 mb-6 text-center">Choose the tax regime for your simulation. This will determine available invoice and tax options.</p>
      <div class="flex gap-6 w-full justify-center">
        <button class="flex-1 px-6 py-4 rounded-xl border-2 border-emerald-300 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-bold text-lg shadow transition-all focus:outline-none focus:ring-2 focus:ring-emerald-400" on:click={() => handleTaxTemplateSelect('gst')}>
          <span class="material-symbols-rounded text-2xl align-middle mr-2">receipt_long</span> GST
        </button>
        <button class="flex-1 px-6 py-4 rounded-xl border-2 border-purple-300 bg-purple-50 hover:bg-purple-100 text-purple-800 font-bold text-lg shadow transition-all focus:outline-none focus:ring-2 focus:ring-purple-400" on:click={() => handleTaxTemplateSelect('vat')}>
          <span class="material-symbols-rounded text-2xl align-middle mr-2">account_balance</span> VAT
        </button>
        <button class="flex-1 px-6 py-4 rounded-xl border-2 border-blue-300 bg-blue-50 hover:bg-blue-100 text-blue-800 font-bold text-lg shadow transition-all focus:outline-none focus:ring-2 focus:ring-blue-400" on:click={() => handleTaxTemplateSelect('plain')}>
          <span class="material-symbols-rounded text-2xl align-middle mr-2">description</span> Plain
        </button>
      </div>
    </div>
  </div>
{/if}

<Toast 
  message={toastMessage}
  type={toastType}
  onClose={handleToastClose}
/>

<style>
  /* Import Inter font */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  
  .font-inter {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  /* Component-specific styles */
  .material-symbols-rounded {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  }
</style>

