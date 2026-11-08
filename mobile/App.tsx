import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Alert,
} from "react-native";
import { MobilSahaSenkronServisi, SahaOlcumKaydi } from "./src/services/offline-sync";

const senkronServisi = new MobilSahaSenkronServisi("http://localhost:8000/api/v1");

export default function App() {
  const [sporcuAdi, setSporcuAdi] = useState("Ali Demo");
  const [testAdi, setTestAdi] = useState("Durarak Uzun Atlama");
  const [hamDeger, setHamDeger] = useState("145");
  const [kuyruk, setKuyruk] = useState<SahaOlcumKaydi[]>([]);
  const [senkronizasyonDurumu, setSenkronizasyonDurumu] = useState("");

  const olcumEkle = () => {
    if (!sporcuAdi || !testAdi || !hamDeger) {
      Alert.alert("Eksik Bilgi", "Lütfen sporcu adı, test ve değeri girin.");
      return;
    }

    const yeniKayit = {
      gecici_id: `mob-${Date.now()}`,
      sporcu_adi: sporcuAdi,
      test_adi: testAdi,
      tarih: new Date().toLocaleDateString("tr-TR"),
      test_yasi: 10,
      oturum: "Mobil Saha Ölçüm Oturumu",
      yer: "Spor Salonu",
      olcumler: { "Deneme 1 (cm)": parseFloat(hamDeger) || 0 },
    };

    senkronServisi.olcumKuyrugaEkle(yeniKayit);
    setKuyruk([...senkronServisi.bekleyenKayitlar()]);
    Alert.alert("Kuyruğa Eklendi", "Ölçüm yerel çevrimdışı hafızaya kaydedildi.");
  };

  const sunucuyaGonder = async () => {
    try {
      setSenkronizasyonDurumu("Senkronize ediliyor...");
      // Demo antrenör token'ı ile senkronize et
      const res = await senkronServisi.sunucuIleSenkronizeEt("mock-token-antrenor", "merkez");
      setKuyruk([...senkronServisi.bekleyenKayitlar()]);
      setSenkronizasyonDurumu(`✓ ${res.islenen_kayit_sayisi} kayıt yerli sunucuya aktarıldı.`);
    } catch (err: any) {
      setSenkronizasyonDurumu("✕ Senkronizasyon hatası (Bağlantı kontrol edin)");
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
          <Text style={styles.title}>PerformTest Mobil</Text>
          <Text style={styles.subtitle}>Saha Çevrimdışı (Offline-First) Ölçüm</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Yeni Saha Ölçümü</Text>

          <Text style={styles.label}>Sporcu Adı</Text>
          <TextInput
            style={styles.input}
            value={sporcuAdi}
            onChangeText={setSporcuAdi}
            placeholder="Örn: Ali Demo"
            placeholderTextColor="#64748b"
          />

          <Text style={styles.label}>Test Protokolü</Text>
          <TextInput
            style={styles.input}
            value={testAdi}
            onChangeText={setTestAdi}
            placeholder="Örn: Durarak Uzun Atlama"
            placeholderTextColor="#64748b"
          />

          <Text style={styles.label}>Ölçülen Değer</Text>
          <TextInput
            style={styles.input}
            value={hamDeger}
            onChangeText={setHamDeger}
            keyboardType="numeric"
            placeholder="Örn: 145"
            placeholderTextColor="#64748b"
          />

          <TouchableOpacity style={styles.button} onPress={olcumEkle}>
            <Text style={styles.buttonText}>+ Çevrimdışı Kuyruğa Kaydet</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.card}>
          <View style={styles.kuyrukHeader}>
            <Text style={styles.cardTitle}>Bekleyen Ölçümler ({kuyruk.length})</Text>
            <TouchableOpacity style={styles.syncButton} onPress={sunucuyaGonder}>
              <Text style={styles.syncButtonText}>Sunucuya Aktar</Text>
            </TouchableOpacity>
          </View>

          {senkronizasyonDurumu ? (
            <Text style={styles.statusText}>{senkronizasyonDurumu}</Text>
          ) : null}

          {kuyruk.map((k) => (
            <View key={k.gecici_id} style={styles.kuyrukItem}>
              <Text style={styles.kuyrukSporcu}>{k.sporcu_adi}</Text>
              <Text style={styles.kuyrukDetay}>
                {k.test_adi}: {JSON.stringify(k.olcumler)}
              </Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#090d16",
  },
  scroll: {
    padding: 20,
  },
  header: {
    marginBottom: 24,
    alignItems: "center",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#38bdf8",
  },
  subtitle: {
    fontSize: 13,
    color: "#94a3b8",
    marginTop: 4,
  },
  card: {
    backgroundColor: "#0f172a",
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: "#1e293b",
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#f8fafc",
    marginBottom: 12,
  },
  label: {
    fontSize: 12,
    fontWeight: "600",
    color: "#94a3b8",
    marginBottom: 4,
  },
  input: {
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 10,
    padding: 10,
    color: "#f8fafc",
    fontSize: 14,
    marginBottom: 12,
  },
  button: {
    backgroundColor: "#2563eb",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginTop: 6,
  },
  buttonText: {
    color: "#ffffff",
    fontWeight: "bold",
    fontSize: 14,
  },
  kuyrukHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  syncButton: {
    backgroundColor: "#10b981",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  syncButtonText: {
    color: "#ffffff",
    fontWeight: "bold",
    fontSize: 12,
  },
  statusText: {
    fontSize: 12,
    color: "#38bdf8",
    marginBottom: 8,
  },
  kuyrukItem: {
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#1e293b",
  },
  kuyrukSporcu: {
    color: "#f8fafc",
    fontWeight: "bold",
    fontSize: 13,
  },
  kuyrukDetay: {
    color: "#94a3b8",
    fontSize: 12,
    marginTop: 2,
  },
});

