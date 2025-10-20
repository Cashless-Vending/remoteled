package com.example.remoteled.adapters;

import android.graphics.drawable.Drawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;

import com.example.remoteled.R;
import com.example.remoteled.models.Service;

import java.util.ArrayList;
import java.util.List;

public class ProductAdapter extends RecyclerView.Adapter<ProductAdapter.ProductViewHolder> {
    
    private List<Service> services;
    private int selectedPosition = -1;
    private OnProductSelectedListener listener;
    
    public interface OnProductSelectedListener {
        void onProductSelected(Service service, int position);
    }
    
    public ProductAdapter(OnProductSelectedListener listener) {
        this.services = new ArrayList<>();
        this.listener = listener;
    }
    
    public void setServices(List<Service> services) {
        this.services = services;
        notifyDataSetChanged();
    }
    
    public Service getSelectedService() {
        if (selectedPosition >= 0 && selectedPosition < services.size()) {
            return services.get(selectedPosition);
        }
        return null;
    }
    
    @NonNull
    @Override
    public ProductViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_product_card, parent, false);
        return new ProductViewHolder(view);
    }
    
    @Override
    public void onBindViewHolder(@NonNull ProductViewHolder holder, int position) {
        Service service = services.get(position);
        holder.bind(service, position == selectedPosition);
    }
    
    @Override
    public int getItemCount() {
        return services.size();
    }
    
    class ProductViewHolder extends RecyclerView.ViewHolder {
        CardView productCard;
        TextView productName;
        TextView productTypeBadge;
        TextView productPrice;
        TextView productDescription;
        TextView ledIndicator;
        
        public ProductViewHolder(@NonNull View itemView) {
            super(itemView);
            productCard = itemView.findViewById(R.id.product_card);
            productName = itemView.findViewById(R.id.product_name);
            productTypeBadge = itemView.findViewById(R.id.product_type_badge);
            productPrice = itemView.findViewById(R.id.product_price);
            productDescription = itemView.findViewById(R.id.product_description);
            ledIndicator = itemView.findViewById(R.id.led_indicator);
        }
        
        public void bind(Service service, boolean isSelected) {
            // Set product name based on type
            String name = getProductName(service);
            productName.setText(name);
            
            // Set type badge
            productTypeBadge.setText(service.getType());
            setBadgeStyle(service.getType());
            
            // Set price
            productPrice.setText(service.getFormattedPrice());
            
            // Set description
            productDescription.setText(service.getDescription());
            
            // Set LED indicator
            ledIndicator.setText(service.getLedIndicator());
            
            // Handle selection state
            if (isSelected) {
                productCard.setCardBackgroundColor(
                    ContextCompat.getColor(itemView.getContext(), R.color.card_selected));
                productCard.setStrokeColor(
                    ContextCompat.getColor(itemView.getContext(), R.color.border_selected));
                productCard.setStrokeWidth(4);
            } else {
                productCard.setCardBackgroundColor(
                    ContextCompat.getColor(itemView.getContext(), R.color.card_background));
                productCard.setStrokeColor(
                    ContextCompat.getColor(itemView.getContext(), R.color.border_default));
                productCard.setStrokeWidth(0);
            }
            
            // Handle click
            productCard.setOnClickListener(v -> {
                int previousPosition = selectedPosition;
                selectedPosition = getAdapterPosition();
                
                notifyItemChanged(previousPosition);
                notifyItemChanged(selectedPosition);
                
                if (listener != null) {
                    listener.onProductSelected(service, selectedPosition);
                }
            });
        }
        
        private String getProductName(Service service) {
            switch (service.getType()) {
                case "TRIGGER":
                    return "Quick Dispense";
                case "FIXED":
                    return "Standard Cycle";
                case "VARIABLE":
                    return "Extended Time";
                default:
                    return "Service";
            }
        }
        
        private void setBadgeStyle(String type) {
            int bgRes, textColorRes;
            
            switch (type) {
                case "TRIGGER":
                    bgRes = R.drawable.badge_trigger;
                    textColorRes = R.color.badge_trigger_text;
                    break;
                case "FIXED":
                    bgRes = R.drawable.badge_fixed;
                    textColorRes = R.color.badge_fixed_text;
                    break;
                case "VARIABLE":
                    bgRes = R.drawable.badge_variable;
                    textColorRes = R.color.badge_variable_text;
                    break;
                default:
                    bgRes = R.drawable.badge_fixed;
                    textColorRes = R.color.badge_fixed_text;
            }
            
            productTypeBadge.setBackground(ContextCompat.getDrawable(itemView.getContext(), bgRes));
            productTypeBadge.setTextColor(ContextCompat.getColor(itemView.getContext(), textColorRes));
        }
    }
}




